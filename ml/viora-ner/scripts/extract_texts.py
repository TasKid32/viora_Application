#!/usr/bin/env python3
"""
Step 1: Extract raw texts from all data sources.
Reads train.json (Kaggle) + HF annotated CVs, discards old labels,
deduplicates, and saves clean raw_texts.jsonl for Gemini re-annotation.
"""

import json
import hashlib
import os
import re
import argparse
from pathlib import Path


def clean_text(text: str) -> str:
    """Remove surrogate characters and normalize whitespace."""
    # Remove surrogate characters (e.g. \ud83d) that can't be encoded as UTF-8
    text = re.sub(r'[\ud800-\udfff]', '', text)
    # Normalize whitespace (but preserve newlines for structure)
    text = re.sub(r'[^\S\n]+', ' ', text)
    # Remove excessive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def extract_kaggle_texts(kaggle_path: str) -> list[dict]:
    """Extract texts from Kaggle train.json"""
    print(f"[Kaggle] Reading {kaggle_path}...")
    with open(kaggle_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for i, sample in enumerate(data):
        text = clean_text(sample.get("text", ""))
        if len(text) < 50:  # Skip tiny texts
            continue
        results.append({
            "id": f"kaggle_{i}",
            "source": "kaggle",
            "text": text,
            "text_hash": hashlib.md5(text.encode("utf-8")).hexdigest(),
        })

    print(f"[Kaggle] Extracted {len(results)} texts (from {len(data)} samples)")
    return results


def extract_hf_texts(hf_dir: str) -> list[dict]:
    """Extract texts from HuggingFace annotated resume JSONs"""
    hf_path = Path(hf_dir)
    json_files = sorted(hf_path.glob("*.json"))
    print(f"[HF] Found {len(json_files)} JSON files in {hf_dir}")

    results = []
    skipped_empty = 0
    skipped_short = 0
    errors = 0

    for jf in json_files:
        try:
            # Skip files that are clearly empty (31 bytes = empty JSON)
            if jf.stat().st_size <= 100:
                skipped_empty += 1
                continue

            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Handle both dict and list formats
            if isinstance(data, list):
                if len(data) == 0:
                    skipped_empty += 1
                    continue
                text = data[0].get("text", "") if isinstance(data[0], dict) else ""
            elif isinstance(data, dict):
                text = data.get("text", "")
            else:
                skipped_empty += 1
                continue

            text = clean_text(text)
            if len(text) < 50:
                skipped_short += 1
                continue

            results.append({
                "id": f"hf_{jf.stem}",
                "source": "hf",
                "text": text,
                "text_hash": hashlib.md5(text.encode("utf-8")).hexdigest(),
            })
        except (json.JSONDecodeError, UnicodeDecodeError, KeyError) as e:
            errors += 1
            continue

    print(f"[HF] Extracted {len(results)} texts")
    print(f"[HF] Skipped: {skipped_empty} empty, {skipped_short} short, {errors} errors")
    return results


def deduplicate(texts: list[dict]) -> list[dict]:
    """Remove duplicate texts by MD5 hash"""
    seen = set()
    unique = []
    for t in texts:
        h = t["text_hash"]
        if h not in seen:
            seen.add(h)
            unique.append(t)
    removed = len(texts) - len(unique)
    print(f"[Dedup] Removed {removed} duplicates, {len(unique)} unique texts remain")
    return unique


def main():
    parser = argparse.ArgumentParser(description="Extract raw texts for re-annotation")
    parser.add_argument(
        "--data-dir",
        default="data",
        help="Base data directory (default: data)",
    )
    parser.add_argument(
        "--output",
        default="data/processed/raw_texts.jsonl",
        help="Output JSONL path",
    )
    args = parser.parse_args()

    base = Path(args.data_dir)

    # --- Extract from both sources ---
    all_texts = []

    # 1. Kaggle NER
    kaggle_path = base / "raw" / "kaggle_ner" / "train.json"
    if kaggle_path.exists():
        all_texts.extend(extract_kaggle_texts(str(kaggle_path)))
    else:
        print(f"[WARN] Kaggle train.json not found at {kaggle_path}")

    # 2. HF Annotated Resumes
    hf_dir = base / "raw" / "hf_annotated_resumes" / "ResumesJsonAnnotated"
    if hf_dir.exists():
        all_texts.extend(extract_hf_texts(str(hf_dir)))
    else:
        print(f"[WARN] HF resumes directory not found at {hf_dir}")

    print(f"\n[Total] {len(all_texts)} texts before deduplication")

    # --- Deduplicate ---
    unique_texts = deduplicate(all_texts)

    # --- Print statistics ---
    sources = {}
    lengths = []
    for t in unique_texts:
        src = t["source"]
        sources[src] = sources.get(src, 0) + 1
        lengths.append(len(t["text"]))

    print(f"\n{'='*60}")
    print(f"  EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"  Total unique texts: {len(unique_texts)}")
    for src, count in sorted(sources.items()):
        print(f"  Source '{src}': {count}")
    if lengths:
        lengths.sort()
        print(f"  Text length: min={min(lengths)}, max={max(lengths)}, "
              f"median={lengths[len(lengths)//2]}, mean={sum(lengths)//len(lengths)}")
    print(f"{'='*60}\n")

    # --- Save output ---
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", encoding="utf-8") as f:
        for t in unique_texts:
            f.write(json.dumps(t, ensure_ascii=False) + "\n")

    print(f"[DONE] Saved {len(unique_texts)} texts to {out_path}")
    print(f"       File size: {out_path.stat().st_size / 1024 / 1024:.1f} MB")


if __name__ == "__main__":
    main()
