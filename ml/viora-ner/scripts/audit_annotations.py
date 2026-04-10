"""
Viora NER — Audit annotation quality in JSONL files.

Detects 5 error patterns:
1. Repetition inconsistency: same text tagged differently in same resume
2. Entity-BIO mismatch: entity in 'entities' list but not in bio_tags
3. Section headers as entities: "EDUCATION", "SKILLS" etc. tagged as entities
4. Single-char entities: single character tagged as SKILL
5. Invalid BIO transitions: I- tag without matching B- prefix

Usage:
    python scripts/audit_annotations.py --input data/processed/annotated.jsonl
    python scripts/audit_annotations.py --input data/processed/annotated.jsonl --output audit_report.json
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

# ── Constants ──────────────────────────────────────────────

# Common CV section headers that should NEVER be entities
SECTION_HEADERS = {
    # Uppercase variants
    "EDUCATION", "EXPERIENCE", "SKILLS", "SUMMARY", "OBJECTIVE",
    "WORK EXPERIENCE", "PROFESSIONAL EXPERIENCE", "TECHNICAL SKILLS",
    "CERTIFICATIONS", "PROJECTS", "ACHIEVEMENTS", "AWARDS",
    "LANGUAGES", "INTERESTS", "HOBBIES", "REFERENCES",
    "PERSONAL INFORMATION", "PERSONAL DETAILS", "CONTACT",
    "PROFESSIONAL SUMMARY", "CAREER OBJECTIVE", "KEY SKILLS",
    "CORE COMPETENCIES", "PROFESSIONAL SKILLS", "QUALIFICATIONS",
    "ACADEMIC QUALIFICATIONS", "ADDITIONAL INFORMATION",
    "WORK HISTORY", "EMPLOYMENT HISTORY", "TRAINING",
    # Title-case variants
    "Education", "Experience", "Skills", "Summary", "Objective",
    "Work Experience", "Professional Experience", "Technical Skills",
    "Certifications", "Projects", "Achievements", "Awards",
    "Languages", "Interests", "Hobbies", "References",
    "Personal Information", "Contact", "Training",
    # With colons/special
    "Role:", "Role", "Skills:", "Education:", "Experience:",
    "Responsibilities:", "Duties:", "Description:",
    # Common patterns that are NOT entities
    "Programming language", "Programming languages",
    "Operating system", "Operating systems",
    "Database", "Databases", "Framework", "Frameworks",
    "Tool", "Tools", "Technology", "Technologies",
    "Soft Skills", "Hard Skills",
}
SECTION_HEADERS_LOWER = {h.lower().strip(":").strip() for h in SECTION_HEADERS}

# Add the labels vocabulary for validation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
try:
    from src.labels import LABEL2ID, BIO_LABELS
except ImportError:
    # Fallback if import fails
    BIO_LABELS = ["O"] + [
        f"{prefix}-{ent}"
        for ent in ["SKILL", "CREDENTIAL", "ORG", "PERSON",
                     "LOCATION", "CONTACT", "JOB_TITLE", "EXPERIENCE"]
        for prefix in ["B", "I"]
    ]
    LABEL2ID = {lbl: i for i, lbl in enumerate(BIO_LABELS)}


def _flatten(lst: list) -> list[str]:
    """Flatten nested lists and ensure all elements are strings."""
    result = []
    for item in lst:
        if isinstance(item, list):
            result.extend(_flatten(item))
        else:
            result.append(str(item))
    return result


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
                    # Malformed pair — skip
                    tokens.append("")
                    tags.append("O")
            record["tokens"] = tokens
            record["bio_tags"] = tags
        else:
            # Already flat list — ensure strings
            record["bio_tags"] = [str(v) for v in bio_tags]

    # Ensure tokens are strings if they exist separately
    tokens = record.get("tokens", [])
    if tokens and isinstance(tokens, list):
        record["tokens"] = [str(v) for v in tokens]

    return record


def extract_entities_from_bio(tokens: list[str], bio_tags: list[str]) -> list[dict]:
    """Extract entity spans from BIO-tagged token/tag pairs."""
    entities = []
    current_entity = None

    for i, (token, tag) in enumerate(zip(tokens, bio_tags)):
        if tag.startswith("B-"):
            # Save previous entity
            if current_entity:
                entities.append(current_entity)
            label = tag[2:]
            current_entity = {
                "text": token,
                "label": label,
                "start_idx": i,
                "end_idx": i,
            }
        elif tag.startswith("I-") and current_entity:
            label = tag[2:]
            if label == current_entity["label"]:
                current_entity["text"] += " " + token
                current_entity["end_idx"] = i
            else:
                # I- tag doesn't match current entity — save and reset
                entities.append(current_entity)
                current_entity = None
        else:
            if current_entity:
                entities.append(current_entity)
                current_entity = None

    if current_entity:
        entities.append(current_entity)

    return entities


def check_repetition_inconsistency(record: dict) -> list[dict]:
    """Check if same text is tagged differently within a resume."""
    errors = []
    tokens = record.get("tokens", [])
    bio_tags = record.get("bio_tags", [])

    if not tokens or not bio_tags or len(tokens) != len(bio_tags):
        return errors

    # Extract all entities
    entities = extract_entities_from_bio(tokens, bio_tags)

    # Group by text (lowercase)
    text_to_labels = defaultdict(set)
    for ent in entities:
        text_to_labels[ent["text"].lower()].add(ent["label"])

    # Also check text that appears as O somewhere but entity elsewhere
    entity_texts_lower = {ent["text"].lower() for ent in entities}

    # Simple check: scan for known entity texts appearing as O
    for i, (token, tag) in enumerate(zip(tokens, bio_tags)):
        if tag == "O" and token.lower() in entity_texts_lower:
            # Check it's a single-token entity match
            for ent in entities:
                if ent["text"].lower() == token.lower() and len(ent["text"].split()) == 1:
                    errors.append({
                        "type": "repetition_inconsistency",
                        "text": token,
                        "detail": f"'{token}' tagged as {ent['label']} at position {ent['start_idx']} but O at position {i}",
                    })
                    break  # one error per occurrence

    return errors


def check_entity_bio_mismatch(record: dict) -> list[dict]:
    """Check if entities list matches bio_tags."""
    errors = []
    entities_list = record.get("entities", [])
    tokens = record.get("tokens", [])
    bio_tags = record.get("bio_tags", [])

    if not entities_list or not bio_tags:
        return errors

    # Extract entities from bio_tags
    bio_entities = extract_entities_from_bio(tokens, bio_tags)
    bio_texts = {ent["text"].lower() for ent in bio_entities}

    # Check each declared entity
    for ent in entities_list:
        text = ent.get("text", "").lower().strip()
        if text and text not in bio_texts:
            errors.append({
                "type": "entity_bio_mismatch",
                "text": ent.get("text", ""),
                "detail": f"Entity '{ent.get('text', '')}' ({ent.get('label', '?')}) in entities list but not found in bio_tags",
            })

    return errors


def check_section_headers(record: dict) -> list[dict]:
    """Check if section headers are incorrectly tagged as entities."""
    errors = []
    tokens = record.get("tokens", [])
    bio_tags = record.get("bio_tags", [])

    if not tokens or not bio_tags:
        return errors

    entities = extract_entities_from_bio(tokens, bio_tags)

    for ent in entities:
        text_clean = ent["text"].strip().strip(":").strip()
        if text_clean.lower() in SECTION_HEADERS_LOWER:
            errors.append({
                "type": "section_header_as_entity",
                "text": ent["text"],
                "detail": f"Section header '{ent['text']}' incorrectly tagged as {ent['label']}",
            })

    return errors


def check_single_char_entities(record: dict) -> list[dict]:
    """Check for single-character SKILL entities."""
    errors = []
    tokens = record.get("tokens", [])
    bio_tags = record.get("bio_tags", [])

    if not tokens or not bio_tags:
        return errors

    entities = extract_entities_from_bio(tokens, bio_tags)

    for ent in entities:
        text = ent["text"].strip()
        if len(text) <= 1 and ent["label"] == "SKILL":
            errors.append({
                "type": "single_char_entity",
                "text": text,
                "detail": f"Single-character SKILL entity: '{text}'",
            })

    return errors


def check_bio_transitions(record: dict) -> list[dict]:
    """Check for invalid BIO tag transitions."""
    errors = []
    bio_tags = record.get("bio_tags", [])

    if not bio_tags:
        return errors

    prev_tag = "O"
    for i, tag in enumerate(bio_tags):
        # Check tag is in vocabulary
        if tag not in LABEL2ID:
            errors.append({
                "type": "invalid_label",
                "text": tag,
                "detail": f"Label '{tag}' at position {i} not in LABEL2ID vocabulary",
            })
            prev_tag = tag
            continue

        # Check I- follows matching B-
        if tag.startswith("I-"):
            expected_b = "B-" + tag[2:]
            expected_i = tag
            if prev_tag != expected_b and prev_tag != expected_i:
                errors.append({
                    "type": "invalid_bio_transition",
                    "text": tag,
                    "detail": f"I-tag '{tag}' at position {i} follows '{prev_tag}' (expected B-{tag[2:]} or {tag})",
                })

        prev_tag = tag

    return errors


def audit_file(input_path: str, max_samples: int = 20) -> dict:
    """Run full audit on a JSONL file."""
    print(f" Auditing: {input_path}")

    records = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
                record["_line_num"] = line_num
                records.append(record)
            except json.JSONDecodeError:
                print(f"    Invalid JSON at line {line_num}")

    total_records = len(records)
    print(f"   Total records: {total_records}")

    # Run all checks
    all_errors = []
    records_with_errors = set()
    errors_by_type = Counter()

    for record in records:
        record = sanitize_record(record)
        record_errors = []
        record_errors.extend(check_repetition_inconsistency(record))
        record_errors.extend(check_entity_bio_mismatch(record))
        record_errors.extend(check_section_headers(record))
        record_errors.extend(check_single_char_entities(record))
        record_errors.extend(check_bio_transitions(record))

        if record_errors:
            records_with_errors.add(record["_line_num"])
            for err in record_errors:
                err["line_num"] = record["_line_num"]
                err["record_id"] = record.get("id", record.get("source", f"line_{record['_line_num']}"))
                errors_by_type[err["type"]] += 1
                all_errors.append(err)

    # Build report
    report = {
        "input_file": str(input_path),
        "total_records": total_records,
        "records_with_errors": len(records_with_errors),
        "error_rate": round(len(records_with_errors) / total_records, 4) if total_records > 0 else 0,
        "total_errors": len(all_errors),
        "errors_by_type": dict(errors_by_type.most_common()),
        "sample_errors": all_errors[:max_samples],
    }

    # Print summary
    print(f"\n{'=' * 50}")
    print(f" AUDIT REPORT")
    print(f"{'=' * 50}")
    print(f"  Total records:       {total_records}")
    print(f"  Records with errors: {len(records_with_errors)} ({report['error_rate'] * 100:.1f}%)")
    print(f"  Total errors:        {len(all_errors)}")
    print(f"\n  Errors by type:")
    for etype, count in errors_by_type.most_common():
        print(f"    {etype}: {count}")

    if all_errors[:5]:
        print(f"\n  Sample errors (first 5):")
        for err in all_errors[:5]:
            print(f"    [{err['type']}] line {err['line_num']}: {err['detail']}")

    return report


def main():
    parser = argparse.ArgumentParser(description="Audit NER annotation quality")
    parser.add_argument("--input", "-i", required=True, help="Path to JSONL file to audit")
    parser.add_argument("--output", "-o", default=None, help="Path to save audit report JSON")
    parser.add_argument("--max-samples", type=int, default=50, help="Max sample errors to include in report")
    args = parser.parse_args()

    report = audit_file(args.input, max_samples=args.max_samples)

    if args.output:
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n Report saved: {args.output}")
    else:
        # Default output next to input
        out = Path(args.input).parent / "audit_report.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n Report saved: {out}")


if __name__ == "__main__":
    main()
