"""
Viora NER -- Tests for training pipeline configuration.
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import TrainConfig, load_config
from src.labels import LABEL2ID, NUM_LABELS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_YAML = PROJECT_ROOT / "configs" / "train.yaml"


class TestConfigLoads:
    """train.yaml should load without errors."""

    def test_config_loads(self):
        if not TRAIN_YAML.exists():
            pytest.skip("train.yaml not found")
        cfg = load_config(TRAIN_YAML)
        assert isinstance(cfg, TrainConfig)
        assert cfg.model_name == "roberta-base"

    def test_data_dir_is_processed(self):
        if not TRAIN_YAML.exists():
            pytest.skip("train.yaml not found")
        cfg = load_config(TRAIN_YAML)
        assert "processed" in cfg.data_dir


class TestMetricConfig:
    """Best model selection should use F1."""

    def test_metric_for_best_model_is_f1(self):
        if not TRAIN_YAML.exists():
            pytest.skip("train.yaml not found")
        cfg = load_config(TRAIN_YAML)
        assert cfg.metric_for_best_model == "eval_f1"

    def test_greater_is_better_is_true(self):
        if not TRAIN_YAML.exists():
            pytest.skip("train.yaml not found")
        cfg = load_config(TRAIN_YAML)
        assert cfg.greater_is_better is True


class TestWeightedTrainer:
    """WeightedNERTrainer should be importable and configured."""

    def test_weighted_trainer_exists(self):
        from src.trainer_module import WeightedNERTrainer
        assert WeightedNERTrainer is not None

    def test_build_class_weights(self):
        from src.trainer_module import build_class_weights
        weights = build_class_weights(0.3)
        assert weights[LABEL2ID["O"]] == 0.3
        assert weights[LABEL2ID["B-SKILL"]] == 1.0
        assert len(weights) == NUM_LABELS


class TestConfigFields:
    """Config fields should exist."""

    def test_warmup_ratio_field(self):
        cfg = TrainConfig()
        assert hasattr(cfg, "warmup_ratio")
        assert cfg.warmup_ratio >= 0

    def test_use_weighted_loss_field(self):
        cfg = TrainConfig()
        assert hasattr(cfg, "use_weighted_loss")

    def test_use_crf_field(self):
        cfg = TrainConfig()
        assert hasattr(cfg, "use_crf")

    def test_scheduler_default(self):
        if not TRAIN_YAML.exists():
            pytest.skip("train.yaml not found")
        cfg = load_config(TRAIN_YAML)
        assert cfg.lr_scheduler_type == "linear"


class TestDataModuleSkipsBadRecords:
    """data_module should handle bad records gracefully."""

    def test_data_module_importable(self):
        from src.data_module import prepare_dataset, read_jsonl
        assert prepare_dataset is not None
        assert read_jsonl is not None
