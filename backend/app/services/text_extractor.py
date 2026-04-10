"""
Text Extractor — Extract text from PDF and DOCX files.

Extracted from file_handler.py for Single Responsibility:
This module handles ONLY text extraction from document files.

Uses PyMuPDF (fitz) for PDF extraction (15x faster than PyPDF2, better Arabic support).
Uses python-docx for DOCX extraction.
"""
import os
from fastapi import HTTPException, status

import pymupdf  # PyMuPDF — installed as `pip install PyMuPDF`
import docx

from app.core.logging import get_logger

logger = get_logger(__name__)


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file using PyMuPDF (fitz).

    Raises:
        ValueError: If text extraction fails completely.
    """
    # Check file size — reject empty files
    if os.path.getsize(file_path) == 0:
        raise ValueError("The uploaded file is empty (0 bytes).")

    text_parts: list[str] = []
    try:
        doc = pymupdf.open(file_path)

        # Check if PDF is password-protected
        if doc.is_encrypted:
            doc.close()
            raise ValueError(
                "This PDF is password-protected. "
                "Please remove the password and re-upload."
            )

        for page in doc:
            page_text = page.get_text("text", sort=True)
            if page_text.strip():
                text_parts.append(page_text)
        doc.close()

        if not text_parts:
            raise ValueError(
                "PDF file contains no extractable text. "
                "The file may be image-based (scanned). "
                "Please upload a text-based PDF or DOCX."
            )

        logger.info(
            "PDF extracted: %d pages, %d chars",
            len(text_parts),
            sum(len(t) for t in text_parts),
        )
    except ValueError:
        raise  # Re-raise our own validation error
    except Exception as e:
        logger.error("Error extracting PDF text: %s", e)
        raise ValueError(f"Failed to read PDF file: {e}")

    return "\n".join(text_parts)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from DOCX file.

    Raises:
        ValueError: If text extraction fails.
    """
    text_parts: list[str] = []
    try:
        document = docx.Document(file_path)
        for paragraph in document.paragraphs:
            if paragraph.text.strip():
                text_parts.append(paragraph.text)

        if not text_parts:
            raise ValueError(
                "DOCX file contains no text. "
                "Please upload a valid resume document."
            )

        logger.info(
            "DOCX extracted: %d paragraphs, %d chars",
            len(text_parts),
            sum(len(t) for t in text_parts),
        )
    except ValueError:
        raise
    except Exception as e:
        logger.error("Error extracting DOCX text: %s", e)
        raise ValueError(f"Failed to read DOCX file: {e}")

    return "\n".join(text_parts)


def extract_text_from_file(file_path: str) -> str:
    """Extract text from file based on extension.

    Raises:
        ValueError: If file type is unsupported or extraction fails.
        HTTPException: If file type is unsupported.
    """
    file_ext = os.path.splitext(file_path)[1].lower()

    if file_ext == ".pdf":
        return extract_text_from_pdf(file_path)
    elif file_ext == ".docx":
        return extract_text_from_docx(file_path)
    elif file_ext == ".doc":
        # python-docx does NOT support old .doc (Office 97-2003)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Old .doc format (Office 97-2003) is not supported. "
                "Please convert to .docx or .pdf and re-upload."
            ),
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}",
        )
