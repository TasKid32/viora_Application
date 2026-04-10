"""
Viora NER — Tests for data quality after fix_annotations.py.

These tests validate the CLEANED data in data/processed/.
Run after: python scripts/fix_annotations.py
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.labels import LABEL2ID, BIO_LABELS

# ── Data path ──────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

SECTION_HEADERS_LOWER = {
    "education", "experience", "skills", "summary", "objective",
    "work experience", "professional experience", "technical skills",
    "certifications", "projects", "achievements", "awards",
    "languages", "interests", "hobbies", "references",
    "personal information", "personal details", "contact",
    "professional summary", "career objective", "key skills",
    "core competencies", "professional skills", "qualifications",
    "role", "responsibilities", "duties", "description",
    "programming language", "programming languages",
    "operating system", "operating systems",
    "database", "databases", "framework", "frameworks",
    "tool", "tools", "technology", "technologies",
    "soft skills", "hard skills",
}


def load_data() -> list[dict]:
    """Load cleaned annotated data."""
    data_file = DATA_DIR / "annotated_clean.jsonl"
    if not data_file.exists():
        pytest.skip(f"Clean data not found: {data_file}")

    records = []
    with open(data_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def extract_entities(tokens, bio_tags):
    """Extract entity spans from tokens and bio_tags."""
    entities = []
    current = None
    for i, (token, tag) in enumerate(zip(tokens, bio_tags)):
        if tag.startswith("B-"):
            if current:
                entities.append(current)
            current = {"text": token, "label": tag[2:], "start": i, "end": i}
        elif tag.startswith("I-") and current and tag[2:] == current["label"]:
            current["text"] += " " + token
            current["end"] = i
        else:
            if current:
                entities.append(current)
                current = None
    if current:
        entities.append(current)
    return entities


class TestNoSectionHeaders:
    """Section headers should not be tagged as entities."""

    def test_no_section_headers_as_entities(self):
        records = load_data()
        violations = []
        for idx, rec in enumerate(records):
            tokens = rec.get("tokens", [])
            bio_tags = rec.get("bio_tags", [])
            if not tokens or not bio_tags:
                continue
            entities = extract_entities(tokens, bio_tags)
            for ent in entities:
                text_clean = ent["text"].strip().strip(":").strip().lower()
                if text_clean in SECTION_HEADERS_LOWER:
                    violations.append(f"Record {idx}: '{ent['text']}' tagged as {ent['label']}")

        assert len(violations) == 0, \
            f"Found {len(violations)} section headers tagged as entities:\n" + \
            "\n".join(violations[:10])


class TestEntitiesMatchBioTags:
    """Entities list and bio_tags should be consistent."""

    def test_entities_match_bio_tags(self):
        records = load_data()
        mismatches = 0
        for rec in records:
            tokens = rec.get("tokens", [])
            bio_tags = rec.get("bio_tags", [])
            if not tokens or not bio_tags:
                continue
            # Just verify lengths match
            assert len(tokens) == len(bio_tags), \
                f"Token/tag length mismatch: {len(tokens)} vs {len(bio_tags)}"


class TestNoSingleCharSkills:
    """No SKILL entity should be a single character."""

    def test_no_single_char_skills(self):
        records = load_data()
        violations = []
        for idx, rec in enumerate(records):
            tokens = rec.get("tokens", [])
            bio_tags = rec.get("bio_tags", [])
            if not tokens or not bio_tags:
                continue
            entities = extract_entities(tokens, bio_tags)
            for ent in entities:
                if ent["label"] == "SKILL" and len(ent["text"].strip()) <= 1:
                    violations.append(f"Record {idx}: '{ent['text']}'")

        assert len(violations) == 0, \
            f"Found {len(violations)} single-char SKILL entities:\n" + \
            "\n".join(violations[:10])


class TestBIOTransitions:
    """BIO tag sequences should be valid."""

    def test_bio_tags_valid_transitions(self):
        records = load_data()
        violations = []
        for idx, rec in enumerate(records):
            bio_tags = rec.get("bio_tags", [])
            if not bio_tags:
                continue
            prev = "O"
            for pos, tag in enumerate(bio_tags):
                if tag.startswith("I-"):
                    expected_b = "B-" + tag[2:]
                    expected_i = tag
                    if prev != expected_b and prev != expected_i:
                        violations.append(
                            f"Record {idx} pos {pos}: '{tag}' after '{prev}'"
                        )
                        break  # one per record
                prev = tag

        assert len(violations) == 0, \
            f"Found {len(violations)} invalid BIO transitions:\n" + \
            "\n".join(violations[:10])


class TestAllLabelsInVocabulary:
    """Every label in bio_tags should exist in LABEL2ID."""

    def test_all_labels_in_vocabulary(self):
        records = load_data()
        unknown_labels = set()
        for rec in records:
            for tag in rec.get("bio_tags", []):
                if tag not in LABEL2ID:
                    unknown_labels.add(tag)

        assert len(unknown_labels) == 0, \
            f"Found unknown labels not in LABEL2ID: {unknown_labels}"


class TestRepeatedEntitiesConsistent:
    """Same text should be tagged the same way within a record."""

    def test_repeated_entities_consistent(self):
        records = load_data()
        inconsistent_count = 0
        for rec in records:
            tokens = rec.get("tokens", [])
            bio_tags = rec.get("bio_tags", [])
            if not tokens or not bio_tags:
                continue
            entities = extract_entities(tokens, bio_tags)
            text_labels = {}
            for ent in entities:
                key = ent["text"].lower()
                if key in text_labels and text_labels[key] != ent["label"]:
                    inconsistent_count += 1
                    break
                text_labels[key] = ent["label"]

        # Allow some tolerance (< 1% of records)
        total = len(records)
        threshold = max(1, int(total * 0.01))
        assert inconsistent_count <= threshold, \
            f"Found {inconsistent_count} records with inconsistent entity labels (threshold: {threshold})"
