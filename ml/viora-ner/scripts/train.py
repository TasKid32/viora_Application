"""
Viora NER -- Training entry point.

Single-stage fine-tuning with class-weighted loss for RoBERTa NER.

Usage:
    python scripts/train.py --config configs/train.yaml
"""

from __future__ import annotations

import logging
import sys
import time
import warnings
from pathlib import Path

# Suppress HuggingFace warnings for cleaner output
import transformers
transformers.logging.set_verbosity_error()
logging.getLogger("transformers.modeling_utils").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", message=".*warmup_ratio.*")
warnings.filterwarnings("ignore", message=".*HF_TOKEN.*")

# Ensure project root is in path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import parse_args_and_load
from src.metrics import get_classification_report
from src.trainer_module import build_trainer


def train():
    """Main training function. Works in both CLI and Colab/Jupyter."""

    sep = "=" * 64
    thin = "-" * 64

    print(sep)
    print("  Viora NER -- Training")
    print(sep)

    # Load config (YAML + CLI overrides)
    cfg = parse_args_and_load()

    print(f"\n  Configuration:")
    print(thin)
    print(f"   Model:          {cfg.model_name}")
    print(f"   Epochs:         {cfg.epochs}")
    print(f"   LR:             {cfg.learning_rate}")
    eff_batch = cfg.per_device_train_batch_size * cfg.gradient_accumulation_steps
    print(f"   Batch (eff):    {cfg.per_device_train_batch_size} x {cfg.gradient_accumulation_steps} = {eff_batch}")
    print(f"   Max Length:     {cfg.max_length}")
    print(f"   Stride:         {cfg.stride}")
    if cfg.warmup_ratio > 0:
        print(f"   Warmup Ratio:   {cfg.warmup_ratio}")
    else:
        print(f"   Warmup Steps:   {cfg.warmup_steps}")
    print(f"   Scheduler:      {cfg.lr_scheduler_type}")
    print(f"   Weighted Loss:  {getattr(cfg, 'use_weighted_loss', False)}")
    ls = getattr(cfg, 'label_smoothing_factor', 0.0)
    if ls > 0:
        print(f"   Label Smooth:   {ls}")
    print(f"   Best Metric:    {cfg.metric_for_best_model}")
    print(f"   Early Stop:     patience={cfg.early_stopping_patience}")
    print(f"   Output:         {cfg.output_dir}")
    print(thin)

    # Build trainer (single-stage, standard fine-tuning)
    trainer, info = build_trainer(cfg)
    tokenizer = info["tokenizer"]

    # -- Train --
    print(f"\n{sep}")
    print("  TRAINING")
    print(sep)

    start = time.time()
    train_result = trainer.train()
    elapsed = time.time() - start

    print(f"\n  Training time: {elapsed / 60:.1f} minutes")
    print(f"  Final train loss: {train_result.training_loss:.4f}")

    # -- Evaluate on validation set --
    print(f"\n  Evaluating on validation set...")
    val_metrics = trainer.evaluate()
    print(f"   Val F1:        {val_metrics.get('eval_f1', 0):.4f}")
    print(f"   Val Precision: {val_metrics.get('eval_precision', 0):.4f}")
    print(f"   Val Recall:    {val_metrics.get('eval_recall', 0):.4f}")

    # -- Evaluate on test set --
    from src.data_module import prepare_dataset
    test_ds = prepare_dataset(cfg.test_path, tokenizer, cfg.max_length, cfg.stride, eval_mode=True)
    print(f"\n  Evaluating on test set ({len(test_ds)} chunks)...")
    test_metrics = trainer.evaluate(test_ds, metric_key_prefix="test")
    print(f"   Test F1:        {test_metrics.get('test_f1', 0):.4f}")
    print(f"   Test Precision: {test_metrics.get('test_precision', 0):.4f}")
    print(f"   Test Recall:    {test_metrics.get('test_recall', 0):.4f}")

    # -- Detailed per-entity report on test set --
    print(f"\n  Per-entity classification report (test):")
    test_preds = trainer.predict(test_ds)
    report_str = get_classification_report(test_preds)
    print(report_str)

    # -- Save best model --
    best_dir = Path(cfg.output_dir) / "best_model"
    best_dir.mkdir(parents=True, exist_ok=True)
    trainer.save_model(str(best_dir))
    tokenizer.save_pretrained(str(best_dir))
    print(f"\n  Best model saved to: {best_dir}")

    # -- Summary --
    f1 = test_metrics.get("test_f1", 0)
    print(f"\n{sep}")
    print(f"  Final Test F1: {f1:.4f}")
    print(f"{sep}\n")

    # Return for Colab usage
    log = {
        "train_loss": train_result.training_loss,
        "val_metrics": val_metrics,
        "test_metrics": test_metrics,
        "training_time_min": elapsed / 60,
    }

    return trainer.model, log


if __name__ == "__main__":
    train()
