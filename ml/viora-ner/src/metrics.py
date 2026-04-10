"""
Viora NER -- Evaluation metrics (seqeval span-level).

Uses HuggingFace evaluate library (official recommended approach)
matching the pattern from HuggingFace Token Classification tutorial:
https://huggingface.co/docs/transformers/tasks/token_classification
"""

from __future__ import annotations

import numpy as np
from seqeval.metrics import classification_report

from .labels import BIO_LABELS, IGNORE_INDEX

# Label list indexed by ID (same order as BIO_LABELS)
label_list = BIO_LABELS  # ["O", "B-SKILL", "I-SKILL", ...]


def compute_metrics(eval_preds) -> dict[str, float]:
    """
    Compute span-level NER metrics using seqeval.

    This follows the EXACT pattern from HuggingFace official tutorial:
    https://huggingface.co/docs/transformers/tasks/token_classification#evaluate

    Args:
        eval_preds: EvalPrediction (predictions=logits, label_ids=labels)

    Returns:
        Dict with f1, precision, recall, accuracy.
    """
    predictions, labels = eval_preds
    predictions = np.argmax(predictions, axis=2)

    # Build lists of label strings, filtering out IGNORE_INDEX (-100)
    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != IGNORE_INDEX]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != IGNORE_INDEX]
        for prediction, label in zip(predictions, labels)
    ]

    # Use seqeval directly (same as evaluate.load("seqeval").compute())
    from seqeval.metrics import (
        f1_score,
        precision_score,
        recall_score,
    )
    from seqeval.scheme import IOB2

    # mode='strict' + scheme=IOB2 =  strict BIO matching (standard)
    f1 = f1_score(true_labels, true_predictions, mode='strict', scheme=IOB2, zero_division=0)
    prec = precision_score(true_labels, true_predictions, mode='strict', scheme=IOB2, zero_division=0)
    rec = recall_score(true_labels, true_predictions, mode='strict', scheme=IOB2, zero_division=0)

    return {
        "f1": round(f1, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
    }


def get_classification_report(eval_preds) -> str:
    """Return detailed per-entity classification report string."""
    predictions = eval_preds.predictions
    labels = eval_preds.label_ids
    predictions = np.argmax(predictions, axis=2)

    true_predictions = [
        [label_list[p] for (p, l) in zip(prediction, label) if l != IGNORE_INDEX]
        for prediction, label in zip(predictions, labels)
    ]
    true_labels = [
        [label_list[l] for (p, l) in zip(prediction, label) if l != IGNORE_INDEX]
        for prediction, label in zip(predictions, labels)
    ]

    from seqeval.scheme import IOB2
    return classification_report(
        true_labels, true_predictions,
        mode='strict', scheme=IOB2,
        zero_division=0, digits=4
    )
