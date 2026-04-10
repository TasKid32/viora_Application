"""
Viora NER -- Label definitions for NER (BIO scheme).

8 entity types × 2 (B-/I-) + O = 17 labels.
"""

# ── Entity types ───────────────────────────────────────────
ENTITY_TYPES = [
    "SKILL",
    "CREDENTIAL",
    "ORG",
    "PERSON",
    "LOCATION",
    "CONTACT",
    "JOB_TITLE",
    "EXPERIENCE",
]

# ── BIO labels ─────────────────────────────────────────────
BIO_LABELS: list[str] = ["O"]
for ent in ENTITY_TYPES:
    BIO_LABELS.append(f"B-{ent}")
    BIO_LABELS.append(f"I-{ent}")

NUM_LABELS = len(BIO_LABELS)  # 17

# ── Mapping dicts ──────────────────────────────────────────
LABEL2ID: dict[str, int] = {lbl: i for i, lbl in enumerate(BIO_LABELS)}
ID2LABEL: dict[int, str] = {i: lbl for i, lbl in enumerate(BIO_LABELS)}

# ── Special index for ignored tokens (subwords, special tokens) ──
IGNORE_INDEX = -100
