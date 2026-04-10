"""
Viora NER -- Test model on real CV files.

Extracts text from PDF/DOCX, runs NER inference, and displays results.

Usage:
    python tests/test_cv.py <path_to_cv>
    python tests/test_cv.py tests/example.pdf
    python tests/test_cv.py tests/example.docx
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.inference import load_model, predict_entities


# ── Text Extraction ───────────────────────────────────────

def extract_text_from_pdf(filepath: str) -> str:
    """Extract text from a PDF file using PyMuPDF."""
    import fitz
    doc = fitz.open(filepath)
    pages = []
    for page in doc:
        pages.append(page.get_text())
    doc.close()
    return "\n".join(pages)


def extract_text_from_docx(filepath: str) -> str:
    """Extract text from a DOCX file using python-docx."""
    from docx import Document
    doc = Document(filepath)
    paragraphs = []
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            paragraphs.append(text)
    return "\n".join(paragraphs)


def extract_text(filepath: str) -> str:
    """Extract text from a file based on its extension."""
    ext = Path(filepath).suffix.lower()
    if ext == ".pdf":
        return extract_text_from_pdf(filepath)
    elif ext in (".docx", ".doc"):
        return extract_text_from_docx(filepath)
    elif ext == ".txt":
        return Path(filepath).read_text(encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file format: {ext}")


# ── Display ───────────────────────────────────────────────

ENTITY_COLORS = {
    "PERSON": "cyan",
    "SKILL": "green",
    "JOB_TITLE": "yellow",
    "ORG": "magenta",
    "LOCATION": "blue",
    "CREDENTIAL": "red",
    "CONTACT": "white",
    "EXPERIENCE": "grey",
}


def display_results(entities, text):
    """Display extracted entities in a formatted table."""
    sep = "=" * 70
    thin = "-" * 70

    print(f"\n{sep}")
    print(f"  EXTRACTED ENTITIES ({len(entities)} found)")
    print(sep)

    # Group by entity type
    by_type: dict[str, list] = {}
    for ent in entities:
        if ent.label not in by_type:
            by_type[ent.label] = []
        by_type[ent.label].append(ent)

    # Display order
    order = ["PERSON", "JOB_TITLE", "ORG", "SKILL", "CREDENTIAL",
             "LOCATION", "CONTACT", "EXPERIENCE"]

    for label in order:
        if label not in by_type:
            continue
        ents = by_type[label]
        # Deduplicate by text
        seen = set()
        unique = []
        for e in ents:
            key = e.text.strip().lower()
            if key not in seen:
                seen.add(key)
                unique.append(e)

        print(f"\n  {label} ({len(unique)} unique)")
        print(thin)
        for e in unique:
            conf_bar = int(e.confidence * 10) * "#"
            conf_bar = conf_bar.ljust(10, ".")
            print(f"    [{conf_bar}] {e.confidence:.2f}  {e.text}")

    # Summary
    print(f"\n{sep}")
    print(f"  SUMMARY")
    print(thin)
    total_unique = sum(
        len(set(e.text.strip().lower() for e in ents))
        for ents in by_type.values()
    )
    print(f"    Total entities:  {len(entities)}")
    print(f"    Unique entities: {total_unique}")
    print(f"    Entity types:    {len(by_type)}")
    print(f"    Text length:     {len(text)} chars")
    print(sep)


# ── Main ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Test Viora NER on a real CV")
    parser.add_argument("cv_path", type=str, help="Path to CV file (PDF, DOCX, or TXT)")
    parser.add_argument("--model", type=str,
                        default=str(ROOT / "models" / "checkpoints" / "best_model"),
                        help="Path to trained model directory")
    parser.add_argument("--max-length", type=int, default=512)
    parser.add_argument("--stride", type=int, default=128)
    args = parser.parse_args()

    cv_path = Path(args.cv_path)
    if not cv_path.exists():
        print(f"ERROR: File not found: {cv_path}")
        sys.exit(1)

    sep = "=" * 70

    print(sep)
    print(f"  Viora NER -- CV Analysis")
    print(sep)
    print(f"  File:  {cv_path.name}")
    print(f"  Model: {Path(args.model).name}")

    # Step 1: Extract text
    print(f"\n  Extracting text from {cv_path.suffix.upper()}...")
    text = extract_text(str(cv_path))
    print(f"  Extracted {len(text)} characters")

    # Show first 300 chars
    print(f"\n  Text preview:")
    print(f"  {'-' * 60}")
    preview = text[:300].replace("\n", " | ")
    print(f"  {preview}...")

    # Step 2: Load model
    print(f"\n  Loading model...")
    model, tokenizer = load_model(args.model)
    print(f"  Model loaded successfully")

    # Step 3: Run inference
    print(f"\n  Running NER inference...")
    entities = predict_entities(
        text, model, tokenizer,
        max_length=args.max_length,
        stride=args.stride,
    )

    # Step 4: Display results
    display_results(entities, text)


if __name__ == "__main__":
    main()
