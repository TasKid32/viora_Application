#!/usr/bin/env python3
"""
Viora ML Data Setup Script
===========================
Downloads and extracts the required ML models and datasets.

Usage:
    python setup_ml_data.py

The archive contains (~1.1 GB compressed):
    - ml/viora-ner/models/         (~1.1 GB) - Trained NER models (safetensors, ONNX, quantized ONNX)
    - ml/viora-ner/data/processed/ (~467 MB) - Processed training data (train/val/test splits)
    - ml/viora-ner/data/raw/       (~101 MB) - Raw datasets (Kaggle NER + HuggingFace Resumes)
    - ml/viora-ner/data/cache/     (~1 MB)   - Pre-computed embedding cache
"""

import os
import sys
import zipfile
import subprocess

# ============================================================
# Configuration — UPDATE THESE AFTER UPLOADING TO GOOGLE DRIVE
# ============================================================
GOOGLE_DRIVE_LINK = "https://drive.google.com/file/d/1TA8BA82QIFu5vTQqhH1iUAUKe_ROpgap/view?usp=sharing"
GOOGLE_DRIVE_FILE_ID = "1TA8BA82QIFu5vTQqhH1iUAUKe_ROpgap"
ARCHIVE_NAME = "viora_ml_data.zip"

EXPECTED_DIRS = [
    "ml/viora-ner/models/checkpoints/best_model",
    "ml/viora-ner/models/exported/onnx",
    "ml/viora-ner/models/exported/onnx_quantized",
    "ml/viora-ner/data/processed",
    "ml/viora-ner/data/raw",
]


def get_project_root():
    """Get the project root directory (where this script is located)."""
    return os.path.dirname(os.path.abspath(__file__))


def install_gdown():
    """Install gdown if not already installed."""
    try:
        import gdown  # noqa: F401
        return True
    except ImportError:
        print("📦 Installing gdown (Google Drive downloader)...")
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "gdown"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print("   ✅ gdown installed successfully.\n")
            return True
        except subprocess.CalledProcessError:
            print("   ❌ Failed to install gdown.")
            return False


def download_from_drive(file_id: str, dest_path: str):
    """Download a file from Google Drive using gdown."""
    if not install_gdown():
        print("\n📋 Please install gdown manually:")
        print("   pip install gdown")
        print(f"   Then run this script again.\n")
        print(f"   Or download manually from: {GOOGLE_DRIVE_LINK}")
        return False

    import gdown

    url = f"https://drive.google.com/uc?id={file_id}"
    print(f"📥 Downloading ML data from Google Drive...")
    print(f"   This may take several minutes (~1.1 GB)...\n")

    try:
        gdown.download(url, dest_path, quiet=False)
        if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1_000_000:
            return True
        else:
            print("❌ Download seems incomplete or failed.")
            return False
    except Exception as e:
        print(f"\n❌ Download failed: {e}")
        return False


def extract_archive(archive_path: str, extract_to: str):
    """Extract the zip archive to the project root."""
    print(f"\n📂 Extracting archive...")
    print(f"   Target: {extract_to}\n")

    try:
        with zipfile.ZipFile(archive_path, 'r') as zf:
            total = len(zf.namelist())
            for i, member in enumerate(zf.namelist()):
                zf.extract(member, extract_to)
                if (i + 1) % 500 == 0 or (i + 1) == total:
                    pct = ((i + 1) / total) * 100
                    print(f"   Extracted: {i + 1}/{total} files ({pct:.0f}%)")

        print(f"\n✅ Extraction complete!")
        return True

    except zipfile.BadZipFile:
        print(f"❌ Error: The archive appears to be corrupted.")
        print(f"   Please re-download and try again.")
        return False
    except Exception as e:
        print(f"❌ Error extracting: {e}")
        return False


def verify_installation(project_root: str):
    """Verify that all expected directories exist after extraction."""
    print(f"\n🔍 Verifying installation...")
    all_ok = True
    for dir_path in EXPECTED_DIRS:
        full_path = os.path.join(project_root, dir_path)
        if os.path.exists(full_path):
            file_count = sum(1 for _, _, files in os.walk(full_path) for _ in files)
            print(f"   ✅ {dir_path}/ ({file_count} files)")
        else:
            print(f"   ❌ {dir_path}/ (MISSING)")
            all_ok = False

    return all_ok


def main():
    project_root = get_project_root()
    archive_path = os.path.join(project_root, ARCHIVE_NAME)

    print("=" * 60)
    print("   Viora ML Data Setup")
    print("=" * 60)
    print(f"\n📁 Project root: {project_root}\n")

    # ── Check if data already exists ──
    existing = [d for d in EXPECTED_DIRS if os.path.exists(os.path.join(project_root, d))]
    if len(existing) == len(EXPECTED_DIRS):
        print("✅ All ML data directories already exist!")
        verify_installation(project_root)
        ans = input("\n⚠️  Re-download and overwrite? (y/N): ").strip().lower()
        if ans != 'y':
            print("👋 No changes made.")
            return

    # ── Check if archive already exists locally ──
    if os.path.exists(archive_path):
        size_mb = os.path.getsize(archive_path) / (1024 * 1024)
        print(f"📦 Found existing archive: {ARCHIVE_NAME} ({size_mb:.1f} MB)")
        ans = input("   Use this file? (Y/n): ").strip().lower()
        if ans == 'n':
            os.remove(archive_path)

    # ── Download if needed ──
    if not os.path.exists(archive_path):
        if GOOGLE_DRIVE_FILE_ID == "PLACEHOLDER_ID":
            print("━" * 60)
            print("  ❌ Google Drive link has not been configured yet.")
            print("━" * 60)
            print(f"\n📋 Manual setup:")
            print(f"   1. Download 'viora_ml_data.zip' from the Google Drive link")
            print(f"      provided in the project README.md")
            print(f"   2. Place the zip file in: {project_root}")
            print(f"   3. Run this script again: python setup_ml_data.py")
            print(f"\n   Or extract manually into the project root so these exist:")
            for d in EXPECTED_DIRS:
                print(f"     • {d}/")
            return

        success = download_from_drive(GOOGLE_DRIVE_FILE_ID, archive_path)
        if not success:
            print(f"\n📋 Manual download alternative:")
            print(f"   1. Visit: {GOOGLE_DRIVE_LINK}")
            print(f"   2. Download 'viora_ml_data.zip'")
            print(f"   3. Place it in: {project_root}")
            print(f"   4. Run this script again")
            return

    # ── Extract ──
    success = extract_archive(archive_path, project_root)
    if not success:
        return

    # ── Verify ──
    all_ok = verify_installation(project_root)

    # ── Cleanup ──
    if all_ok:
        print(f"\n🎉 ML data setup complete! All files are in place.")
        ans = input(f"\n🗑️  Delete archive to save ~1.1 GB? (Y/n): ").strip().lower()
        if ans != 'n':
            os.remove(archive_path)
            print(f"   Deleted {ARCHIVE_NAME}")
    else:
        print(f"\n⚠️  Some directories are missing. The archive may be incomplete.")

    print(f"\n👋 Done!")


if __name__ == "__main__":
    main()
