"""
Viora NER -- Configuration loader.

Loads YAML config into a dataclass with CLI override support.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class TrainConfig:
    """All training parameters in one place."""

    # Model
    model_name: str = "roberta-base"

    # Data
    data_dir: str = "data/processed"
    train_file: str = "train.jsonl"
    val_file: str = "val.jsonl"
    test_file: str = "test.jsonl"
    label_info_file: str = "label_info.json"
    max_length: int = 512
    stride: int = 128

    # Training
    output_dir: str = "models/checkpoints"
    epochs: int = 15
    per_device_train_batch_size: int = 4
    per_device_eval_batch_size: int = 8
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-5
    warmup_steps: int = 0
    warmup_ratio: float = 0.06
    weight_decay: float = 0.01
    max_grad_norm: float = 1.0
    lr_scheduler_type: str = "cosine"
    seed: int = 42
    o_class_weight: float = 0.3

    # Weighted loss & CRF
    use_weighted_loss: bool = True
    use_crf: bool = False
    label_smoothing_factor: float = 0.0

    # Evaluation & Saving
    eval_strategy: str = "epoch"
    save_strategy: str = "epoch"
    save_total_limit: int = 3
    load_best_model_at_end: bool = True
    metric_for_best_model: str = "eval_f1"
    greater_is_better: bool = True

    # Early stopping
    early_stopping_patience: int = 3

    # Logging
    logging_steps: int = 50
    report_to: str = "none"

    # ── Derived paths ──────────────────────────────────────
    @property
    def train_path(self) -> Path:
        return Path(self.data_dir) / self.train_file

    @property
    def val_path(self) -> Path:
        return Path(self.data_dir) / self.val_file

    @property
    def test_path(self) -> Path:
        return Path(self.data_dir) / self.test_file


def load_config(yaml_path: str | Path) -> TrainConfig:
    """Load config from a YAML file, returning a TrainConfig dataclass."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    cfg = TrainConfig()
    for key, val in raw.items():
        if hasattr(cfg, key):
            setattr(cfg, key, val)
    return cfg


def parse_args_and_load() -> TrainConfig:
    """Parse CLI args, load YAML, and allow CLI overrides."""
    parser = argparse.ArgumentParser(description="Viora NER Training")
    parser.add_argument("--config", type=str, default="configs/train.yaml",
                        help="Path to YAML config file")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--batch_size", type=int, default=None)
    parser.add_argument("--output_dir", type=str, default=None)
    parser.add_argument("--model_name", type=str, default=None)

    args, _unknown = parser.parse_known_args()

    # Load from YAML
    cfg = load_config(args.config)

    # CLI overrides
    if args.epochs is not None:
        cfg.epochs = args.epochs
    if args.lr is not None:
        cfg.learning_rate = args.lr
    if args.batch_size is not None:
        cfg.per_device_train_batch_size = args.batch_size
    if args.output_dir is not None:
        cfg.output_dir = args.output_dir
    if args.model_name is not None:
        cfg.model_name = args.model_name

    return cfg
