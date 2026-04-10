"""
Viora NER -- Custom training callbacks.

- NaNStopCallback: halt training on NaN/Inf loss or gradients
"""

from __future__ import annotations

import math

from transformers import TrainerCallback, TrainerControl, TrainerState
from transformers import TrainingArguments as HfTrainingArguments


class NaNStopCallback(TrainerCallback):
    """Immediately stop training if loss or grad_norm is NaN/Inf."""

    def on_log(
        self,
        args: HfTrainingArguments,
        state: TrainerState,
        control: TrainerControl,
        logs: dict | None = None,
        **kwargs,
    ):
        if logs is None:
            return

        loss = logs.get("loss", None)
        grad_norm = logs.get("grad_norm", None)

        if loss is not None and (math.isnan(loss) or math.isinf(loss)):
            print(f"\n[ERROR] NaN/Inf loss detected at step {state.global_step}: {loss}")
            print("   Stopping training immediately.")
            control.should_training_stop = True

        if grad_norm is not None and (math.isnan(grad_norm) or math.isinf(grad_norm)):
            print(f"\n[ERROR] NaN/Inf grad_norm detected at step {state.global_step}: {grad_norm}")
            print("   Stopping training immediately.")
            control.should_training_stop = True

        # Also stop if loss explodes (> 100)
        if loss is not None and loss > 100:
            print(f"\n[WARN] Loss too high at step {state.global_step}: {loss}")
            print("   Stopping training.")
            control.should_training_stop = True
