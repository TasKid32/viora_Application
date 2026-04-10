"""
File Upload — Save uploaded files to disk with validation.

Extracted from file_handler.py for Single Responsibility:
This module handles ONLY file upload + disk persistence.
"""
import os
from fastapi import UploadFile, HTTPException, status
from pathlib import Path
from datetime import datetime

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file to disk and return the file path.

    Validates file size against MAX_FILE_SIZE before saving.

    Raises:
        HTTPException: If file exceeds size limit.
    """
    # Create uploads directory if not exists
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Read file content and check size
    content = await upload_file.read()
    file_size = len(content)

    if file_size > settings.MAX_FILE_SIZE:
        max_mb = settings.MAX_FILE_SIZE / (1024 * 1024)
        actual_mb = file_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"File too large: {actual_mb:.1f}MB. "
                f"Maximum allowed: {max_mb:.0f}MB."
            ),
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    # Generate unique filename
    timestamp = int(datetime.now().timestamp() * 1000)
    filename = f"{timestamp}_{upload_file.filename}"
    file_path = upload_dir / filename

    # Save file
    with file_path.open("wb") as buffer:
        buffer.write(content)

    logger.info("File saved: %s (%d bytes)", filename, file_size)
    return str(file_path)
