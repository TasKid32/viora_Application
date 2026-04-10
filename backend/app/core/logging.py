"""
Structured logging configuration for Viora Backend.

Usage:
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("User registered", extra={"user_id": user.id})
"""
import logging
import sys
from app.core.config import settings


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name, typically __name__ of the calling module.

    Returns:
        Configured logger with appropriate formatting.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        handler.setLevel(log_level)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(log_level)

    return logger
