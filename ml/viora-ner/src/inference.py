"""
Viora NER -- Inference module for production use.

Tokenizes text the SAME way as training (is_split_into_words=True)
to avoid BPE subword fragmentation issues.

Supports both PyTorch and ONNX models, with sliding window for long texts.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForTokenClassification

from .labels import ID2LABEL, IGNORE_INDEX


@dataclass
class Entity:
    """A detected entity in the text."""
    text: str
    label: str
    start: int
    end: int
    confidence: float = 0.0


def load_model(
    model_path: str | Path,
    use_onnx: bool = False,
) -> tuple[Any, AutoTokenizer]:
    """Load model and tokenizer from a saved directory."""
    tokenizer = AutoTokenizer.from_pretrained(
        model_path,
        use_fast=True,
        add_prefix_space=True,
    )

    if use_onnx:
        from optimum.onnxruntime import ORTModelForTokenClassification

        # Auto-detect quantized model file name
        model_dir = Path(model_path)
        if (model_dir / "model_quantized.onnx").exists():
            model = ORTModelForTokenClassification.from_pretrained(
                model_path, file_name="model_quantized.onnx"
            )
        else:
            model = ORTModelForTokenClassification.from_pretrained(model_path)
    else:
        model = AutoModelForTokenClassification.from_pretrained(model_path)
        model.eval()

    return model, tokenizer


# ── Word splitting (same as data_module.py) ───────────────

def _split_into_words(text: str) -> tuple[list[str], list[tuple[int, int]]]:
    """
    Split text by whitespace, then split off leading/trailing brackets
    and strip bullet characters from word starts.

    Why? Training data contains pre-cleaned tokens ("Phlebotomy"),
    but real CV text has punctuation attached ("(Phlebotomy)").
    This causes the tokenizer to produce different subwords:
      Training:  "Phlebotomy"   → first subword ĠPh  (model recognizes)
      Inference: "(Phlebotomy)" → first subword Ġ(   (model can't recognize)

    By splitting off brackets and stripping bullets, the tokenizer sees
    clean words that match the training distribution.

    Character spans are preserved correctly so entity positions
    still point to the right locations in the original text.
    """
    # Characters that should be split off as separate tokens
    _BRACKET_OPEN = set("([{")
    _BRACKET_CLOSE = set(")]}")
    # Bullet/list marker characters to strip (not meaningful for NER)
    _BULLET_CHARS = set("\u2022\u25cf\u25a0\u25aa\u25ba\u2023\u2013\u2014\u2010")
    #                    •       ●       ■       ▪       ►       ‣       –       —       ‐

    # ── Phase 1: basic whitespace splitting ───────────────
    raw_tokens: list[tuple[str, int, int]] = []
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        start = i
        while i < n and not text[i].isspace():
            i += 1
        raw_tokens.append((text[start:i], start, i))

    # ── Phase 2: split off brackets, strip bullets ────────
    words: list[str] = []
    spans: list[tuple[int, int]] = []

    for word, start, end in raw_tokens:
        # Strip leading bullet characters (discard — they are list markers)
        while word and word[0] in _BULLET_CHARS:
            start += 1
            word = word[1:]

        # Split off leading brackets as separate tokens
        while word and word[0] in _BRACKET_OPEN:
            words.append(word[0])
            spans.append((start, start + 1))
            start += 1
            word = word[1:]

        # Collect trailing brackets to add AFTER the main word
        trailing: list[tuple[str, int, int]] = []
        while word and word[-1] in _BRACKET_CLOSE:
            end -= 1
            trailing.append((word[-1], end, end + 1))
            word = word[:-1]

        # Add the main word (if anything remains after stripping)
        if word:
            words.append(word)
            spans.append((start, end))

        # Add trailing brackets in correct text order (reversed from strip order)
        for bword, bstart, bend in reversed(trailing):
            words.append(bword)
            spans.append((bstart, bend))

    return words, spans


# ── Main inference function ───────────────────────────────

def predict_entities(
    text: str,
    model: Any,
    tokenizer: AutoTokenizer,
    max_length: int = 512,
    stride: int = 128,
    use_onnx: bool = False,
) -> list[Entity]:
    """
    Run NER inference on a text and return detected entities.

    Uses the SAME tokenization strategy as training:
      1. Split text into words (whitespace)
      2. Tokenize with is_split_into_words=True
      3. Use word_ids() to map subwords back to words
      4. Take prediction of first subword per word (same as training)
      5. Reconstruct entities using word character spans
    """
    # Step 1: Split text into words with character positions
    words, word_spans = _split_into_words(text)

    if not words:
        return []

    # Step 2: Tokenize with is_split_into_words=True (same as training)
    encoding = tokenizer(
        words,
        is_split_into_words=True,
        max_length=max_length,
        truncation=True,
        padding=False,
        return_overflowing_tokens=True,
        stride=stride,
    )

    num_chunks = len(encoding["input_ids"])

    # Step 3: Get word-level predictions from each chunk
    # word_preds[word_idx] = list of (label_id, confidence) from all chunks
    word_preds: dict[int, list[tuple[int, float]]] = {}

    for chunk_idx in range(num_chunks):
        # Get input tensors for this chunk
        input_ids = encoding["input_ids"][chunk_idx]
        attention_mask = encoding["attention_mask"][chunk_idx]

        if use_onnx:
            inputs = {
                "input_ids": np.array([input_ids]),
                "attention_mask": np.array([attention_mask]),
            }
            logits = model(**inputs).logits
            if isinstance(logits, torch.Tensor):
                logits = logits.numpy()
            probs = _softmax(logits[0])
        else:
            inputs = {
                "input_ids": torch.tensor([input_ids]),
                "attention_mask": torch.tensor([attention_mask]),
            }
            with torch.no_grad():
                outputs = model(**inputs)
                probs = torch.softmax(outputs.logits[0], dim=-1).numpy()

        # Use word_ids() to map subwords to words (same as training)
        wids = encoding.word_ids(batch_index=chunk_idx)
        prev_wid = None

        for tok_idx, wid in enumerate(wids):
            if wid is None:
                # Special token (CLS, SEP, PAD) -- skip
                continue

            if wid != prev_wid:
                # First subword of this word -- take its prediction
                # (same logic as training: only first subword gets a label)
                pred_id = int(np.argmax(probs[tok_idx]))
                confidence = float(probs[tok_idx][pred_id])

                if wid not in word_preds:
                    word_preds[wid] = []
                word_preds[wid].append((pred_id, confidence))

            prev_wid = wid

    # Step 4: Aggregate predictions per word (highest confidence wins)
    word_labels: list[tuple[str, float]] = []  # (label, confidence) per word
    for w_idx in range(len(words)):
        if w_idx in word_preds:
            preds = word_preds[w_idx]
            best_pred, best_conf = max(preds, key=lambda x: x[1])
            label = ID2LABEL.get(best_pred, "O")
            word_labels.append((label, best_conf))
        else:
            word_labels.append(("O", 0.0))

    # Step 5: Merge consecutive words into entities using BIO tags
    entities: list[Entity] = []
    current_label = None
    current_start = 0
    current_end = 0
    current_confs: list[float] = []

    for w_idx, (label, conf) in enumerate(word_labels):
        char_start, char_end = word_spans[w_idx]

        if label.startswith("B-"):
            # Flush previous entity
            if current_label:
                entities.append(Entity(
                    text=text[current_start:current_end],
                    label=current_label,
                    start=current_start,
                    end=current_end,
                    confidence=sum(current_confs) / len(current_confs),
                ))
            current_label = label[2:]
            current_start = char_start
            current_end = char_end
            current_confs = [conf]

        elif label.startswith("I-") and current_label == label[2:]:
            # Continue current entity
            current_end = char_end
            current_confs.append(conf)

        else:
            # O label or label mismatch -- flush
            if current_label:
                entities.append(Entity(
                    text=text[current_start:current_end],
                    label=current_label,
                    start=current_start,
                    end=current_end,
                    confidence=sum(current_confs) / len(current_confs),
                ))
            current_label = None
            current_confs = []

    # Flush last entity
    if current_label:
        entities.append(Entity(
            text=text[current_start:current_end],
            label=current_label,
            start=current_start,
            end=current_end,
            confidence=sum(current_confs) / len(current_confs),
        ))

    return entities


def _softmax(x: np.ndarray) -> np.ndarray:
    """Numerically stable softmax."""
    e = np.exp(x - np.max(x, axis=-1, keepdims=True))
    return e / e.sum(axis=-1, keepdims=True)
