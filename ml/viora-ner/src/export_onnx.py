"""
Viora NER -- ONNX export with INT8 dynamic quantization.

Usage:
    from src.export_onnx import export_model
    export_model("models/checkpoints/best_model", "models/exported")
"""

from __future__ import annotations

from pathlib import Path


def export_model(
    model_path: str | Path,
    output_dir: str | Path,
    quantize: bool = True,
) -> Path:
    """
    Export a fine-tuned model to ONNX format.

    Args:
        model_path: Path to the fine-tuned model directory.
        output_dir: Where to save the ONNX model.
        quantize: Whether to also create INT8 quantized version.

    Returns:
        Path to the exported ONNX model directory.
    """
    # Lazy imports so this module doesn't break if optimum isn't installed
    from optimum.onnxruntime import ORTModelForTokenClassification, ORTQuantizer
    from optimum.onnxruntime.configuration import AutoQuantizationConfig

    model_path = Path(model_path)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    onnx_dir = output_dir / "onnx"
    quant_dir = output_dir / "onnx_quantized"

    # ── Step 1: Export to ONNX ─────────────────────────────
    print(f"Exporting ONNX from: {model_path}")
    ort_model = ORTModelForTokenClassification.from_pretrained(
        model_path,
        export=True,
    )
    ort_model.save_pretrained(onnx_dir)
    print(f"   ONNX saved to: {onnx_dir}")

    # Copy tokenizer files
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    tokenizer.save_pretrained(onnx_dir)

    if quantize:
        # ── Step 2: INT8 Dynamic Quantization ──────────────
        print(f"Quantizing to INT8...")
        quantizer = ORTQuantizer.from_pretrained(onnx_dir)
        qconfig = AutoQuantizationConfig.avx512_vnni(
            is_static=False,
            per_channel=False,
        )
        quantizer.quantize(save_dir=quant_dir, quantization_config=qconfig)

        # Copy tokenizer to quantized dir too
        tokenizer.save_pretrained(quant_dir)
        print(f"   Quantized model saved to: {quant_dir}")

        # Report sizes
        onnx_size = sum(f.stat().st_size for f in onnx_dir.rglob("*.onnx"))
        quant_size = sum(f.stat().st_size for f in quant_dir.rglob("*.onnx"))
        print(f"\nSize comparison:")
        print(f"   ONNX:      {onnx_size / 1024 / 1024:.1f} MB")
        print(f"   Quantized: {quant_size / 1024 / 1024:.1f} MB")
        print(f"   Reduction: {(1 - quant_size / onnx_size) * 100:.0f}%")

    return output_dir


def validate_onnx(
    pytorch_model_path: str | Path,
    onnx_model_path: str | Path,
    sample_text: str = "John Smith is a Senior Software Engineer at Google in New York",
) -> dict:
    """
    Compare PyTorch vs ONNX model outputs on a sample to verify correctness.
    """
    import numpy as np
    import torch
    from transformers import AutoModelForTokenClassification, AutoTokenizer
    from optimum.onnxruntime import ORTModelForTokenClassification

    tokenizer = AutoTokenizer.from_pretrained(pytorch_model_path)
    inputs = tokenizer(sample_text, return_tensors="pt", padding=True, truncation=True)

    # PyTorch prediction
    pt_model = AutoModelForTokenClassification.from_pretrained(pytorch_model_path)
    pt_model.eval()
    with torch.no_grad():
        pt_logits = pt_model(**inputs).logits.numpy()

    # ONNX prediction
    ort_model = ORTModelForTokenClassification.from_pretrained(onnx_model_path)
    ort_logits = ort_model(**inputs).logits.numpy()

    # Compare
    max_diff = np.max(np.abs(pt_logits - ort_logits))
    preds_match = np.array_equal(np.argmax(pt_logits, axis=-1), np.argmax(ort_logits, axis=-1))

    print(f"Validation:")
    print(f"   Max logit diff:    {max_diff:.6f}")
    print(f"   Predictions match: {'yes' if preds_match else 'no'}")

    return {
        "max_diff": float(max_diff),
        "predictions_match": preds_match,
    }
