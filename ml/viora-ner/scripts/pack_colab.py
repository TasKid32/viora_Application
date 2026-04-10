"""
Viora NER -- Pack project as ZIP for Google Colab.

Creates viora_ner_colab.zip containing:
  - configs/train.yaml
  - src/ (all modules)
  - scripts/train.py, scripts/evaluate.py
  - data/processed/*.jsonl + label_info.json
  - tests/ (quality checks)

Usage:
    python scripts/pack_colab.py
"""

from __future__ import annotations

import zipfile
from pathlib import Path


def pack():
    base = Path(__file__).resolve().parent.parent
    zip_path = base / "viora_ner_colab.zip"

    # Files to include (relative to base)
    files_to_pack = [
        "configs/train.yaml",
        "scripts/train.py",
        "scripts/evaluate.py",
        "data/processed/train_augmented.jsonl",
        "data/processed/val.jsonl",
        "data/processed/test.jsonl",
    ]

    # Check for label_info.json
    label_info = base / "data" / "processed" / "label_info.json"
    if label_info.exists():
        files_to_pack.append("data/processed/label_info.json")

    # Add all src/ Python files
    src_dir = base / "src"
    for py_file in sorted(src_dir.glob("*.py")):
        files_to_pack.append(f"src/{py_file.name}")

    # Add all tests/ Python files
    tests_dir = base / "tests"
    if tests_dir.exists():
        for py_file in sorted(tests_dir.glob("*.py")):
            files_to_pack.append(f"tests/{py_file.name}")

    print("Packing Viora NER for Google Colab...\n")

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel_path in files_to_pack:
            full_path = base / rel_path
            if full_path.exists():
                arc_name = f"viora-ner/{rel_path}"
                zf.write(full_path, arc_name)
                size_kb = full_path.stat().st_size // 1024
                print(f"  + {rel_path} ({size_kb} KB)")
            else:
                print(f"  [MISSING] {rel_path}")

    zip_size = zip_path.stat().st_size / 1024 / 1024
    print(f"\nZIP created: {zip_path}")
    print(f"   Size: {zip_size:.1f} MB")
    print(f"\nUpload to Google Drive, then use in Colab:")
    print(f"   from google.colab import drive")
    print(f"   drive.mount('/content/drive')")
    print(f"   !pip install -q transformers datasets seqeval accelerate pyyaml sentencepiece")
    print(f"   import zipfile")
    print(f"   with zipfile.ZipFile('/content/drive/MyDrive/viora_ner_colab.zip','r') as z:")
    print(f"       z.extractall('/content')")
    print(f"   import os, sys")
    print(f"   os.chdir('/content/viora-ner')")
    print(f"   sys.path.insert(0, '/content/viora-ner')")
    print(f"   !python -m pytest tests/ -v")
    print(f"   from scripts.train import train")
    print(f"   model, log = train()")


if __name__ == "__main__":
    pack()
