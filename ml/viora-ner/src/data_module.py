"""
Viora NER -- Data loading & preprocessing module.

Pipeline:
  1. Read JSONL (text + character-span entities OR pre-split tokens + bio_tags)
  2. Split text into words with character offsets (if needed)
  3. Assign word-level BIO labels from spans (if needed)
  4. Tokenize with is_split_into_words=True + sliding window
  5. Align labels to subword tokens via word_ids()
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
from datasets import Dataset
from transformers import PreTrainedTokenizerBase

from .labels import BIO_LABELS, IGNORE_INDEX, LABEL2ID


# ═══════════════════════════════════════════════════════════
# 1. Read JSONL
# ═══════════════════════════════════════════════════════════

def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    """Read a JSONL file, each line = {"text": ..., "entities": [[s,e,label], ...]}."""
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


# ═══════════════════════════════════════════════════════════
# 2. Word splitting with character offsets
# ═══════════════════════════════════════════════════════════

def split_into_words(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    """
    Split text by whitespace and return (words, char_spans).
    Each span = (start_char, end_char) — end is exclusive.
    """
    words = []
    spans = []
    i = 0
    n = len(text)
    while i < n:
        # skip whitespace
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n and not text[i].isspace():
            i += 1
        words.append(text[start:i])
        spans.append((start, i))
    return words, spans


# ═══════════════════════════════════════════════════════════
# 3. Assign word-level BIO labels
# ═══════════════════════════════════════════════════════════

def assign_bio_labels(
    word_spans: list[tuple[int, int]],
    entities: list[list],
) -> list[str]:
    """
    For each word, determine its BIO label based on entity spans.

    Args:
        word_spans: list of (start, end) char positions for each word.
        entities: list of [start_char, end_char, label] from the data.

    Returns:
        List of BIO label strings, one per word.
    """
    num_words = len(word_spans)
    labels = ["O"] * num_words

    # Sort entities by start position
    sorted_ents = sorted(entities, key=lambda e: e[0])

    for ent_start, ent_end, ent_label in sorted_ents:
        first = True
        for w_idx, (w_start, w_end) in enumerate(word_spans):
            # Check overlap: word overlaps with entity span
            if w_start < ent_end and w_end > ent_start:
                if first:
                    labels[w_idx] = f"B-{ent_label}"
                    first = False
                else:
                    labels[w_idx] = f"I-{ent_label}"

    return labels


# ═══════════════════════════════════════════════════════════
# 4. Tokenize & align labels (with sliding window)
# ═══════════════════════════════════════════════════════════

def tokenize_and_align(
    words: list[str],
    word_labels: list[str],
    tokenizer: PreTrainedTokenizerBase,
    max_length: int = 512,
    stride: int = 128,
) -> list[dict[str, list[int]]]:
    """
    Tokenize a pre-split word list and align BIO labels to subword tokens.

    Uses sliding window (return_overflowing_tokens) for long documents.

    Returns:
        List of dicts, each with keys:
          - input_ids
          - attention_mask
          - labels
    """
    encoding = tokenizer(
        words,
        is_split_into_words=True,
        max_length=max_length,
        truncation=True,
        padding=False,
        return_overflowing_tokens=True,
        stride=stride,
        return_offsets_mapping=False,
    )

    chunks = []
    # encoding can have multiple chunks due to overflow
    num_chunks = len(encoding["input_ids"])

    for chunk_idx in range(num_chunks):
        input_ids = encoding["input_ids"][chunk_idx]
        attention_mask = encoding["attention_mask"][chunk_idx]
        word_ids = encoding.word_ids(batch_index=chunk_idx)

        aligned_labels = []
        prev_word_id = None

        for wid in word_ids:
            if wid is None:
                # Special tokens ([CLS], [SEP], padding)
                aligned_labels.append(IGNORE_INDEX)
            elif wid != prev_word_id:
                # First subword of a new word → use the word's label
                label_str = word_labels[wid]
                aligned_labels.append(LABEL2ID.get(label_str, LABEL2ID["O"]))
            else:
                # Continuation subword → ignore
                aligned_labels.append(IGNORE_INDEX)
            prev_word_id = wid

        chunks.append({
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "labels": aligned_labels,
        })

    return chunks


# ═══════════════════════════════════════════════════════════
# 5. Full pipeline: JSONL → HuggingFace Dataset
# ═══════════════════════════════════════════════════════════

def prepare_dataset(
    jsonl_path: str | Path,
    tokenizer: PreTrainedTokenizerBase,
    max_length: int = 512,
    stride: int = 128,
    eval_mode: bool = False,
) -> Dataset:
    """
    End-to-end: read JSONL -> tokenize -> Dataset.

    If bio_tags are available (from Groq annotation), use them directly.
    Otherwise, fall back to offset-based BIO assignment.

    Args:
        eval_mode: If True, disables sliding window overlap (truncation only).
                   Prevents duplicate entity counting during evaluation.
    """
    records = read_jsonl(jsonl_path)

    all_input_ids = []
    all_attention_masks = []
    all_labels = []

    used_bio_tags = 0
    used_offsets = 0
    skipped = 0

    for rec_idx, rec in enumerate(records):
        text = rec.get("text", "")
        bio_tags = rec.get("bio_tags", None)
        tokens_field = rec.get("tokens", None)

        try:
            if tokens_field and bio_tags and isinstance(bio_tags, list):
                # ── Separate tokens and bio_tags lists ──
                if isinstance(bio_tags[0], str):
                    words = tokens_field
                    word_labels = bio_tags
                    used_bio_tags += 1
                # ── Paired [[token, tag], ...] format ──
                elif isinstance(bio_tags[0], list):
                    words = [pair[0] for pair in bio_tags]
                    word_labels = [pair[1] for pair in bio_tags]
                    used_bio_tags += 1
                else:
                    skipped += 1
                    continue
            elif bio_tags and isinstance(bio_tags, list) and len(bio_tags) > 0:
                if isinstance(bio_tags[0], list):
                    # Paired format without separate tokens
                    words = [pair[0] for pair in bio_tags]
                    word_labels = [pair[1] for pair in bio_tags]
                    used_bio_tags += 1
                elif isinstance(bio_tags[0], str):
                    # Flat bio_tags without tokens — extract words from text
                    if text:
                        words = text.split()
                        word_labels = bio_tags
                        # Align lengths (text.split may differ from original tokenization)
                        min_len = min(len(words), len(word_labels))
                        words = words[:min_len]
                        word_labels = word_labels[:min_len]
                        used_bio_tags += 1
                    else:
                        skipped += 1
                        continue
                else:
                    skipped += 1
                    continue
            else:
                # ── FALLBACK: Compute BIO from character offsets ──
                entities = rec.get("entities", [])
                if not text:
                    skipped += 1
                    continue
                words, word_spans = split_into_words(text)
                word_labels = assign_bio_labels(word_spans, entities)
                used_offsets += 1

            if not words or not word_labels:
                skipped += 1
                continue

            # Tokenize & align (may produce multiple chunks)
            effective_stride = 0 if eval_mode else stride
            chunks = tokenize_and_align(words, word_labels, tokenizer, max_length, effective_stride)

            for chunk in chunks:
                all_input_ids.append(chunk["input_ids"])
                all_attention_masks.append(chunk["attention_mask"])
                all_labels.append(chunk["labels"])

        except Exception as e:
            skipped += 1
            if skipped <= 3:
                print(f"  [data] [WARN] Skipped record {rec_idx}: {e}")

    print(f"  [data] {len(records)} records → {len(all_input_ids)} chunks")
    print(f"  [data] Used bio_tags: {used_bio_tags}, Used offsets: {used_offsets}, Skipped: {skipped}")

    dataset = Dataset.from_dict({
        "input_ids": all_input_ids,
        "attention_mask": all_attention_masks,
        "labels": all_labels,
    })

    return dataset
