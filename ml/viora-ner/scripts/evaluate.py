"""
Viora NER — Evaluate a saved model on a dataset.

Usage:
    python scripts/evaluate.py --model models/checkpoints/best_model --data data/processed/test.jsonl
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    Trainer,
    TrainingArguments,
)

from src.data_module import prepare_dataset
from src.labels import ID2LABEL, LABEL2ID, NUM_LABELS
from src.metrics import compute_metrics, get_classification_report


def main():
    parser = argparse.ArgumentParser(description="Evaluate a saved NER model")
    parser.add_argument("--model", type=str, required=True,
                        help="Path to saved model directory")
    parser.add_argument("--data", type=str, required=True,
                        help="Path to JSONL evaluation data")
    parser.add_argument("--max_length", type=int, default=512)
    parser.add_argument("--stride", type=int, default=128)
    parser.add_argument("--batch_size", type=int, default=8)
    args = parser.parse_args()

    print(f"\n Model: {args.model}")
    print(f" Data:  {args.data}")

    # Load
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True, add_prefix_space=True)
    model = AutoModelForTokenClassification.from_pretrained(args.model)

    # Prepare dataset
    dataset = prepare_dataset(args.data, tokenizer, args.max_length, args.stride)
    print(f" Chunks: {len(dataset)}")

    # Data collator
    collator = DataCollatorForTokenClassification(tokenizer=tokenizer, padding=True)

    # Trainer for evaluation only
    eval_args = TrainingArguments(
        output_dir="/tmp/eval_output",
        per_device_eval_batch_size=args.batch_size,
        disable_tqdm=True,
        report_to="none",
    )

    trainer = Trainer(
        model=model,
        args=eval_args,
        data_collator=collator,
        compute_metrics=compute_metrics,
    )

    # Evaluate
    print("\n Running evaluation...")
    preds = trainer.predict(dataset)
    metrics = preds.metrics

    print(f"\n   F1:        {metrics.get('test_f1', 0):.4f}")
    print(f"   Precision: {metrics.get('test_precision', 0):.4f}")
    print(f"   Recall:    {metrics.get('test_recall', 0):.4f}")
    print(f"   Macro F1:  {metrics.get('test_macro_f1', 0):.4f}")

    # Detailed report
    print("\n Per-entity classification report:")
    report = get_classification_report(preds)
    print(report)


if __name__ == "__main__":
    main()
