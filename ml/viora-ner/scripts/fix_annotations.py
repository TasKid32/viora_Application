"""
Viora NER — Fix annotation errors automatically.

Takes annotated.jsonl and produces a clean version:
1. Remove section headers tagged as entities
2. Fix repetition inconsistency (propagate majority label)
3. Rebuild bio_tags from fixed entities
4. Remove single-char SKILL entities
5. Validate against gazetteer (optional)
6. Fix invalid BIO transitions

Usage:
    python scripts/fix_annotations.py --input data/processed/annotated.jsonl --output data/processed/annotated_clean.jsonl
"""

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

try:
    from src.labels import LABEL2ID, BIO_LABELS, ENTITY_TYPES
except ImportError:
    ENTITY_TYPES = ["SKILL", "CREDENTIAL", "ORG", "PERSON",
                    "LOCATION", "CONTACT", "JOB_TITLE", "EXPERIENCE"]
    BIO_LABELS = ["O"] + [
        f"{prefix}-{ent}" for ent in ENTITY_TYPES for prefix in ["B", "I"]
    ]
    LABEL2ID = {lbl: i for i, lbl in enumerate(BIO_LABELS)}


# ── Section headers to remove ──────────────────────────────
SECTION_HEADERS_LOWER = {
    "education", "experience", "skills", "summary", "objective",
    "work experience", "professional experience", "technical skills",
    "certifications", "projects", "achievements", "awards",
    "languages", "interests", "hobbies", "references",
    "personal information", "personal details", "contact",
    "professional summary", "career objective", "key skills",
    "core competencies", "professional skills", "qualifications",
    "academic qualifications", "additional information",
    "work history", "employment history", "training",
    "role", "responsibilities", "duties", "description",
    "programming language", "programming languages",
    "operating system", "operating systems",
    "database", "databases", "framework", "frameworks",
    "tool", "tools", "technology", "technologies",
    "soft skills", "hard skills",
}


def sanitize_record(record: dict) -> dict:
    """Sanitize a record to handle various bio_tags formats.

    Supports:
    - Paired format: bio_tags = [[token, tag], [token, tag], ...]
    - Separate format: tokens = [...], bio_tags = [tag, tag, ...]
    """
    bio_tags = record.get("bio_tags", [])

    if bio_tags and isinstance(bio_tags, list):
        # Check if it's paired format: [[token, tag], ...]
        if isinstance(bio_tags[0], list) and len(bio_tags[0]) == 2:
            tokens = []
            tags = []
            for pair in bio_tags:
                if isinstance(pair, list) and len(pair) == 2:
                    tokens.append(str(pair[0]))
                    tags.append(str(pair[1]))
                else:
                    tokens.append("")
                    tags.append("O")
            record["tokens"] = tokens
            record["bio_tags"] = tags
        else:
            record["bio_tags"] = [str(v) for v in bio_tags]

    tokens = record.get("tokens", [])
    if tokens and isinstance(tokens, list):
        record["tokens"] = [str(v) for v in tokens]

    return record


def extract_entities_from_bio(tokens: list[str], bio_tags: list[str]) -> list[dict]:
    """Extract entity spans from token/tag pairs."""
    entities = []
    current = None

    for i, (token, tag) in enumerate(zip(tokens, bio_tags)):
        if tag.startswith("B-"):
            if current:
                entities.append(current)
            current = {
                "label": tag[2:],
                "start": i,
                "end": i,
                "tokens": [token],
            }
        elif tag.startswith("I-") and current and tag[2:] == current["label"]:
            current["end"] = i
            current["tokens"].append(token)
        else:
            if current:
                entities.append(current)
                current = None

    if current:
        entities.append(current)

    for ent in entities:
        ent["text"] = " ".join(ent["tokens"])

    return entities


def rebuild_bio_tags(tokens: list[str], entities: list[dict]) -> list[str]:
    """Rebuild bio_tags from entity list."""
    bio_tags = ["O"] * len(tokens)

    for ent in entities:
        start = ent["start"]
        end = ent["end"]
        label = ent["label"]

        if start < len(bio_tags):
            bio_tags[start] = f"B-{label}"
        for i in range(start + 1, min(end + 1, len(bio_tags))):
            bio_tags[i] = f"I-{label}"

    return bio_tags


def fix_record(record: dict, stats: dict) -> dict | None:
    """Fix a single record. Returns None if record should be dropped."""
    record = sanitize_record(record)
    tokens = record.get("tokens", [])
    bio_tags = record.get("bio_tags", [])

    if not tokens or not bio_tags:
        stats["dropped_no_tokens"] += 1
        return None

    if len(tokens) != len(bio_tags):
        stats["dropped_length_mismatch"] += 1
        return None

    # Step 1: Extract current entities
    entities = extract_entities_from_bio(tokens, bio_tags)

    # Step 2: Remove section headers
    filtered_entities = []
    for ent in entities:
        text_clean = ent["text"].strip().strip(":").strip().lower()
        if text_clean in SECTION_HEADERS_LOWER:
            stats["removed_section_headers"] += 1
            continue
        filtered_entities.append(ent)
    entities = filtered_entities

    # Step 3: Remove single-char SKILL entities
    filtered_entities = []
    for ent in entities:
        if ent["label"] == "SKILL" and len(ent["text"].strip()) <= 1:
            stats["removed_single_char"] += 1
            continue
        filtered_entities.append(ent)
    entities = filtered_entities

    # Step 4: Fix repetition inconsistency
    # For each unique text, find the most common label and apply it consistently
    text_label_counts = defaultdict(lambda: Counter())
    for ent in entities:
        text_lower = ent["text"].lower()
        text_label_counts[text_lower][ent["label"]] += 1

    for ent in entities:
        text_lower = ent["text"].lower()
        counts = text_label_counts[text_lower]
        if len(counts) > 1:
            # Multiple labels for same text — use majority
            majority_label = counts.most_common(1)[0][0]
            if ent["label"] != majority_label:
                stats["fixed_repetition_inconsistency"] += 1
                ent["label"] = majority_label

    # Step 5: Fix invalid BIO transitions by rebuilding tags
    new_bio_tags = rebuild_bio_tags(tokens, entities)

    # Step 6: Validate all tags are in vocabulary
    valid_tags = []
    for tag in new_bio_tags:
        if tag in LABEL2ID:
            valid_tags.append(tag)
        else:
            valid_tags.append("O")
            stats["fixed_invalid_labels"] += 1

    # Build cleaned record
    cleaned = dict(record)
    cleaned["bio_tags"] = valid_tags

    # Also update entities list if present
    if "entities" in cleaned:
        new_entities_list = []
        for ent in entities:
            new_entities_list.append({
                "text": ent["text"],
                "label": ent["label"],
                "start": ent["start"],
                "end": ent["end"],
            })
        cleaned["entities"] = new_entities_list

    stats["records_output"] += 1
    return cleaned


def fix_file(input_path: str, output_path: str) -> dict:
    """Fix all records in a JSONL file."""
    print(f" Fixing annotations: {input_path}")
    print(f"   Output: {output_path}")

    stats = Counter()
    records_in = 0

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(input_path, "r", encoding="utf-8") as fin, \
         open(output_path, "w", encoding="utf-8") as fout:

        for line_num, line in enumerate(fin, 1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                stats["dropped_invalid_json"] += 1
                continue

            records_in += 1
            cleaned = fix_record(record, stats)

            if cleaned is not None:
                # Remove internal metadata
                cleaned.pop("_line_num", None)
                fout.write(json.dumps(cleaned, ensure_ascii=False) + "\n")

    stats["records_input"] = records_in

    # Print summary
    print(f"\n{'=' * 50}")
    print(f" FIX REPORT")
    print(f"{'=' * 50}")
    print(f"  Records in:                    {stats['records_input']}")
    print(f"  Records out:                   {stats['records_output']}")
    print(f"  Dropped (no tokens):           {stats['dropped_no_tokens']}")
    print(f"  Dropped (length mismatch):     {stats['dropped_length_mismatch']}")
    print(f"  Dropped (invalid JSON):        {stats['dropped_invalid_json']}")
    print(f"  Removed section headers:       {stats['removed_section_headers']}")
    print(f"  Removed single-char SKILLs:    {stats['removed_single_char']}")
    print(f"  Fixed repetition inconsistency:{stats['fixed_repetition_inconsistency']}")
    print(f"  Fixed invalid labels:          {stats['fixed_invalid_labels']}")

    return dict(stats)


def main():
    parser = argparse.ArgumentParser(description="Fix NER annotation errors")
    parser.add_argument("--input", "-i", required=True, help="Input JSONL file")
    parser.add_argument("--output", "-o", required=True, help="Output cleaned JSONL file")
    args = parser.parse_args()

    stats = fix_file(args.input, args.output)

    # Save stats
    stats_path = Path(args.output).parent / "fix_stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
    print(f"\n Stats saved: {stats_path}")


if __name__ == "__main__":
    main()
