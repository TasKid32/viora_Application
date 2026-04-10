#!/usr/bin/env python3
"""
Step 3c: Split cleaned data into train/val/test.
Entity-stratified split to ensure balanced entity distribution.
Output format compatible with train.py.
"""

import json
import random
import argparse
from pathlib import Path
from collections import Counter


def get_dominant_label(entities):
    """Get the most common entity label in a sample (for stratification)."""
    if not entities:
        return "NONE"
    counts = Counter(e["label"] for e in entities)
    return counts.most_common(1)[0][0]


def convert_to_train_format(record):
    """Convert annotated format to training format.
    
    From: {"text": ..., "entities": [{"text": ..., "start": N, "end": N, "label": "X"}, ...]}
    To:   {"text": ..., "entities": [[start, end, "LABEL"], ...], "bio_tags": [...]}
    
    CRITICAL: Preserves bio_tags and tokens from cleaned annotation — these are the
    gold-standard pre-aligned word-level BIO tags that should be used directly for training.
    """
    entities = []
    for ent in record.get("entities", []):
        if isinstance(ent, dict):
            entities.append([ent["start"], ent["end"], ent["label"]])
        elif isinstance(ent, list):
            entities.append(ent)
    result = {
        "text": record["text"],
        "entities": entities,
    }
    # Preserve tokens if available (clean format)
    if "tokens" in record and record["tokens"]:
        result["tokens"] = record["tokens"]
    # Preserve bio_tags if available
    if "bio_tags" in record and record["bio_tags"]:
        result["bio_tags"] = record["bio_tags"]
    return result


def stratified_split(records, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, seed=42):
    """Split records with stratification by dominant entity label."""
    random.seed(seed)

    # Group by dominant label
    groups = {}
    for r in records:
        label = get_dominant_label(r.get("entities", []))
        if label not in groups:
            groups[label] = []
        groups[label].append(r)

    train, val, test = [], [], []

    for label, group in groups.items():
        random.shuffle(group)
        n = len(group)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)

        train.extend(group[:n_train])
        val.extend(group[n_train:n_train + n_val])
        test.extend(group[n_train + n_val:])

    # Shuffle each split
    random.shuffle(train)
    random.shuffle(val)
    random.shuffle(test)

    return train, val, test


def print_split_stats(name, records):
    """Print entity distribution for a split."""
    label_counts = Counter()
    for r in records:
        for ent in r.get("entities", []):
            label = ent[2] if isinstance(ent, list) else ent["label"]
            label_counts[label] += 1
    total = sum(label_counts.values())
    print(f"\n  {name}: {len(records)} samples, {total:,} entities")
    for label, count in label_counts.most_common():
        print(f"    {label:<15} {count:>6} ({count/total*100:5.1f}%)")


def main():
    parser = argparse.ArgumentParser(description="Split data")
    parser.add_argument("--input", default="data/processed/annotated_clean.jsonl")
    parser.add_argument("--output-dir", default="data/processed")
    parser.add_argument("--train-ratio", type=float, default=0.8)
    parser.add_argument("--val-ratio", type=float, default=0.1)
    parser.add_argument("--test-ratio", type=float, default=0.1)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    # Load
    all_records = []
    with open(args.input, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                all_records.append(json.loads(line))
    print(f"Loaded {len(all_records)} total records")

    # CRITICAL: Filter out failed records (no bio_tags = corrupted offsets)
    records = [
        r for r in all_records
        if r.get("status") == "ok" and r.get("bio_tags") and len(r["bio_tags"]) > 0
    ]
    dropped = len(all_records) - len(records)
    print(f"Filtered: kept {len(records)}, dropped {dropped} (no bio_tags / failed)")

    # Split
    train, val, test = stratified_split(
        records, args.train_ratio, args.val_ratio, args.test_ratio, args.seed
    )

    # Convert to training format
    train = [convert_to_train_format(r) for r in train]
    val = [convert_to_train_format(r) for r in val]
    test = [convert_to_train_format(r) for r in test]

    # Save
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, data in [("train", train), ("val", val), ("test", test)]:
        path = out_dir / f"{name}.jsonl"
        with open(path, "w", encoding="utf-8") as f:
            for r in data:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print(f"  Saved {path}: {len(data)} samples")

    # Report
    print(f"\n{'='*60}")
    print(f"  SPLIT REPORT")
    print(f"{'='*60}")
    print_split_stats("Train", train)
    print_split_stats("Val", val)
    print_split_stats("Test", test)
    print(f"\n{'='*60}")


if __name__ == "__main__":
    main()
