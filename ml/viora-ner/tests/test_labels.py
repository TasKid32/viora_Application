"""
Viora NER — Tests for label definitions.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.labels import (
    BIO_LABELS,
    ENTITY_TYPES,
    ID2LABEL,
    LABEL2ID,
    NUM_LABELS,
    IGNORE_INDEX,
)


class TestLabelCount:
    """Test that label counts are correct."""

    def test_entity_types_count(self):
        """There should be exactly 8 entity types."""
        assert len(ENTITY_TYPES) == 8

    def test_label_count_is_17(self):
        """8 types × 2 (B/I) + O = 17 labels."""
        assert NUM_LABELS == 17
        assert len(BIO_LABELS) == 17

    def test_o_is_first(self):
        """O label should be at index 0."""
        assert BIO_LABELS[0] == "O"
        assert LABEL2ID["O"] == 0


class TestLabelMappings:
    """Test LABEL2ID and ID2LABEL consistency."""

    def test_label2id_and_id2label_match(self):
        """LABEL2ID[ID2LABEL[i]] == i for all i."""
        for i in range(NUM_LABELS):
            label = ID2LABEL[i]
            assert LABEL2ID[label] == i, f"Mismatch at index {i}: ID2LABEL={label}, LABEL2ID={LABEL2ID.get(label)}"

    def test_id2label_and_label2id_match(self):
        """ID2LABEL[LABEL2ID[lbl]] == lbl for all labels."""
        for lbl in BIO_LABELS:
            idx = LABEL2ID[lbl]
            assert ID2LABEL[idx] == lbl, f"Mismatch for label '{lbl}': LABEL2ID={idx}, ID2LABEL={ID2LABEL.get(idx)}"

    def test_all_labels_in_label2id(self):
        """Every BIO_LABEL has an entry in LABEL2ID."""
        for lbl in BIO_LABELS:
            assert lbl in LABEL2ID, f"Label '{lbl}' missing from LABEL2ID"

    def test_all_ids_in_id2label(self):
        """Every index 0..16 has an entry in ID2LABEL."""
        for i in range(NUM_LABELS):
            assert i in ID2LABEL, f"Index {i} missing from ID2LABEL"


class TestBIOFormat:
    """Test BIO label format validity."""

    def test_all_bio_labels_valid_format(self):
        """Every label starts with B- or I- or equals O."""
        for lbl in BIO_LABELS:
            assert lbl == "O" or lbl.startswith("B-") or lbl.startswith("I-"), \
                f"Invalid label format: '{lbl}'"

    def test_every_entity_has_b_and_i(self):
        """Each entity type has both B- and I- labels."""
        for ent in ENTITY_TYPES:
            assert f"B-{ent}" in LABEL2ID, f"Missing B-{ent}"
            assert f"I-{ent}" in LABEL2ID, f"Missing I-{ent}"

    def test_ignore_index(self):
        """IGNORE_INDEX should be -100 (standard for HuggingFace)."""
        assert IGNORE_INDEX == -100
