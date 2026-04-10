"""
API Quota Handler — monitors external API quota exhaustion.

Instead of rate-limiting users, we let them use freely.
When YouTube/Gemini quotas are exhausted, we catch the errors
and return user-friendly messages.
"""
from fastapi import HTTPException, status
from app.core.logging import get_logger

logger = get_logger(__name__)


class QuotaExhaustedError(HTTPException):
    """Raised when an external API quota is exceeded."""

    def __init__(self, service: str, retry_after: str = "midnight PT"):
        detail = {
            "error": "quota_exceeded",
            "message": f"{service} API quota has been exhausted. Please try again later.",
            "service": service,
            "retry_after": retry_after,
        }
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
        )
        logger.warning("Quota exhausted for service: %s", service)


def handle_youtube_quota_error(error) -> bool:
    """Check if a YouTube API error is a quota exceeded error.

    Returns True if it was a quota error (and raises QuotaExhaustedError).
    Returns False if it was a different error.
    """
    error_str = str(error)
    if "quotaExceeded" in error_str or "dailyLimitExceeded" in error_str:
        raise QuotaExhaustedError(
            service="YouTube",
            retry_after="midnight Pacific Time (PT)",
        )
    return False


def handle_gemini_quota_error(error) -> bool:
    """Check if a Gemini API error is a quota exceeded error.

    Returns True if it was a quota error (and raises QuotaExhaustedError).
    Returns False if it was a different error.
    """
    error_str = str(error)
    if "quota" in error_str.lower() or "429" in error_str:
        raise QuotaExhaustedError(
            service="Gemini AI",
            retry_after="wait a few minutes or until midnight PT",
        )
    return False
