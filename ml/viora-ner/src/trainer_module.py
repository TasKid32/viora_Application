"""
Viora NER -- Trainer module.

Single-stage fine-tuning for NER with optional class-weighted loss.
Uses RoBERTa-base (stable, no NaN issues, bf16 compatible).
"""

from __future__ import annotations

import os
from pathlib import Path

import torch
import torch.nn as nn
from transformers import (
    AutoModelForTokenClassification,
    AutoTokenizer,
    DataCollatorForTokenClassification,
    EarlyStoppingCallback,
    Trainer,
    TrainingArguments,
)

from .callbacks import NaNStopCallback
from .config import TrainConfig
from .data_module import prepare_dataset
from .labels import ID2LABEL, IGNORE_INDEX, LABEL2ID, NUM_LABELS
from .metrics import compute_metrics


# ═══════════════════════════════════════════════════════════
# Weighted NER Trainer (down-weights O class)
# ═══════════════════════════════════════════════════════════

class WeightedNERTrainer(Trainer):
    """Custom Trainer that applies class weights to CrossEntropyLoss.

    Down-weights the O class to focus training on entity tokens.
    """

    def __init__(self, class_weights: torch.Tensor | None = None, **kwargs):
        super().__init__(**kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, **kwargs):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits

        if self.class_weights is not None:
            weight = self.class_weights.to(logits.device)
            loss_fn = nn.CrossEntropyLoss(
                weight=weight,
                ignore_index=IGNORE_INDEX,
            )
        else:
            loss_fn = nn.CrossEntropyLoss(ignore_index=IGNORE_INDEX)

        # logits: (batch, seq_len, num_labels), labels: (batch, seq_len)
        loss = loss_fn(logits.view(-1, NUM_LABELS), labels.view(-1))

        return (loss, outputs) if return_outputs else loss


# ═══════════════════════════════════════════════════════════
# Build class weights
# ═══════════════════════════════════════════════════════════

def build_class_weights(o_weight: float = 0.3) -> torch.Tensor:
    """Build class weights tensor: O gets o_weight, all others get 1.0."""
    weights = torch.ones(NUM_LABELS)
    weights[LABEL2ID["O"]] = o_weight
    return weights


# ═══════════════════════════════════════════════════════════
# Build trainer
# ═══════════════════════════════════════════════════════════

def build_trainer(cfg: TrainConfig) -> tuple:
    """
    Build a HuggingFace Trainer for NER fine-tuning.

    Uses WeightedNERTrainer if use_weighted_loss=True, else standard Trainer.
    """
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # ── Load tokenizer ─────────────────────────────────────
    tokenizer = AutoTokenizer.from_pretrained(
        cfg.model_name,
        use_fast=True,
        add_prefix_space=True,
    )

    # ── Prepare datasets (loaded once) ─────────────────────
    print("  Loading datasets...")
    train_ds = prepare_dataset(cfg.train_path, tokenizer, cfg.max_length, cfg.stride)
    val_ds = prepare_dataset(cfg.val_path, tokenizer, cfg.max_length, cfg.stride, eval_mode=True)
    print(f"   Train chunks: {len(train_ds)}")
    print(f"   Val chunks:   {len(val_ds)}")

    # ── Load model ─────────────────────────────────────────
    print(f"\n  Loading {cfg.model_name}...")
    model = AutoModelForTokenClassification.from_pretrained(
        cfg.model_name,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
    )
    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"   Total params:     {total_params:,}")
    print(f"   Trainable params: {trainable:,}")

    # ── Precision ──────────────────────────────────────────
    bf16, fp16 = False, False
    if torch.cuda.is_available():
        capability = torch.cuda.get_device_capability()
        if capability[0] >= 8:
            bf16 = True
        else:
            fp16 = True
    print(f"   Precision: {'bf16' if bf16 else 'fp16' if fp16 else 'fp32'}")

    # ── Data collator ──────────────────────────────────────
    data_collator = DataCollatorForTokenClassification(
        tokenizer=tokenizer,
        padding=True,
    )

    # ── Training arguments ─────────────────────────────────
    # Support both warmup_ratio and warmup_steps
    warmup_kwargs = {}
    if cfg.warmup_ratio > 0:
        warmup_kwargs["warmup_ratio"] = cfg.warmup_ratio
    elif cfg.warmup_steps > 0:
        warmup_kwargs["warmup_steps"] = cfg.warmup_steps

    training_args = TrainingArguments(
        output_dir=cfg.output_dir,
        num_train_epochs=cfg.epochs,
        per_device_train_batch_size=cfg.per_device_train_batch_size,
        per_device_eval_batch_size=cfg.per_device_eval_batch_size,
        gradient_accumulation_steps=cfg.gradient_accumulation_steps,
        learning_rate=cfg.learning_rate,
        **warmup_kwargs,
        weight_decay=cfg.weight_decay,
        max_grad_norm=cfg.max_grad_norm,
        lr_scheduler_type=cfg.lr_scheduler_type,
        label_smoothing_factor=getattr(cfg, 'label_smoothing_factor', 0.0),
        # Evaluation & saving
        eval_strategy=cfg.eval_strategy,
        save_strategy=cfg.save_strategy,
        save_total_limit=cfg.save_total_limit,
        load_best_model_at_end=cfg.load_best_model_at_end,
        metric_for_best_model=cfg.metric_for_best_model,
        greater_is_better=cfg.greater_is_better,
        # Precision
        bf16=bf16,
        fp16=fp16,
        # Logging
        logging_steps=cfg.logging_steps,
        logging_first_step=True,
        report_to=cfg.report_to,
        log_level="warning",
        # Misc
        seed=cfg.seed,
        disable_tqdm=False,
        dataloader_num_workers=0,
    )

    # ── Callbacks ──────────────────────────────────────────
    callbacks = [
        NaNStopCallback(),
        EarlyStoppingCallback(early_stopping_patience=cfg.early_stopping_patience),
    ]

    # ── Choose Trainer ─────────────────────────────────────
    use_weighted = getattr(cfg, "use_weighted_loss", True)

    if use_weighted:
        class_weights = build_class_weights(cfg.o_class_weight)
        print(f"   Using WeightedNERTrainer (O weight = {cfg.o_class_weight})")
        trainer = WeightedNERTrainer(
            class_weights=class_weights,
            model=model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=val_ds,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
            callbacks=callbacks,
        )
    else:
        print("   Using standard Trainer (no class weighting)")
        trainer = Trainer(
            model=model,
            args=training_args,
            train_dataset=train_ds,
            eval_dataset=val_ds,
            data_collator=data_collator,
            compute_metrics=compute_metrics,
            callbacks=callbacks,
        )

    info = {
        "tokenizer": tokenizer,
        "model": model,
        "train_ds": train_ds,
        "val_ds": val_ds,
    }

    return trainer, info
