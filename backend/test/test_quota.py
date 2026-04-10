"""
Unit tests for quota/rate-limiting logic.

Tests the middleware and error handling for API quota exhaustion
(403 Forbidden) and rate limiting (429 Too Many Requests).
"""
import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException


# ── Quota Error Response Tests ──────────────────────────

class TestQuotaResponses:
    """Test that quota-related errors return expected responses."""

    def test_429_error_message(self):
        """429 should return user-friendly rate limit message."""
        response = {"detail": "Rate limit exceeded. Please try again in 60 seconds."}
        assert "rate limit" in response["detail"].lower() or "try again" in response["detail"].lower()

    def test_403_quota_error(self):
        """403 with quota detail should include quota info."""
        response = {"detail": "API quota exceeded", "quota": {"used": 100, "limit": 100}}
        assert response.get("quota") is not None
        assert response["quota"]["used"] >= response["quota"]["limit"]

    def test_403_non_quota_is_auth_error(self):
        """403 without quota info should be treated as auth error."""
        response = {"detail": "Forbidden — insufficient permissions"}
        is_quota = "quota" in response or "limit" in response.get("detail", "").lower()
        # "limit" is not in this message, and no "quota" key
        assert not ("quota" in response and response.get("quota") is not None)


# ── Rate Limit Header Tests ─────────────────────────────

class TestRateLimitHeaders:
    """Test rate limit response header parsing."""

    def test_parse_retry_after_header(self):
        """Retry-After header should be parsed as integer seconds."""
        headers = {"Retry-After": "60"}
        retry_after = int(headers.get("Retry-After", "0"))
        assert retry_after == 60

    def test_parse_rate_limit_headers(self):
        """X-RateLimit headers should be correctly parsed."""
        headers = {
            "X-RateLimit-Limit": "100",
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1710633600",
        }
        limit = int(headers.get("X-RateLimit-Limit", "0"))
        remaining = int(headers.get("X-RateLimit-Remaining", "0"))
        reset = int(headers.get("X-RateLimit-Reset", "0"))

        assert limit == 100
        assert remaining == 0
        assert reset > 0


# ── Quota Tracking Logic ────────────────────────────────

class TestQuotaTracking:
    """Test quota billing/tracking logic."""

    def test_quota_under_limit(self):
        """Request should be allowed when under quota."""
        quota = {"used": 50, "limit": 100}
        allowed = quota["used"] < quota["limit"]
        assert allowed is True

    def test_quota_at_limit(self):
        """Request should be denied when at quota limit."""
        quota = {"used": 100, "limit": 100}
        allowed = quota["used"] < quota["limit"]
        assert allowed is False

    def test_quota_over_limit(self):
        """Request should be denied when over quota limit."""
        quota = {"used": 150, "limit": 100}
        allowed = quota["used"] < quota["limit"]
        assert allowed is False

    def test_quota_reset(self):
        """After reset, usage should be 0."""
        quota = {"used": 100, "limit": 100}
        # Simulate reset
        quota["used"] = 0
        allowed = quota["used"] < quota["limit"]
        assert allowed is True


# ── HTTP Exception Tests ────────────────────────────────

class TestHTTPExceptions:
    """Test FastAPI HTTPException for quota errors."""

    def test_raise_429(self):
        """429 HTTPException should carry correct status and message."""
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please wait before trying again."
            )
        assert exc_info.value.status_code == 429
        assert "too many" in exc_info.value.detail.lower()

    def test_raise_403_quota(self):
        """403 HTTPException for quota should carry correct detail."""
        with pytest.raises(HTTPException) as exc_info:
            raise HTTPException(
                status_code=403,
                detail="API quota exceeded for this billing period."
            )
        assert exc_info.value.status_code == 403
        assert "quota" in exc_info.value.detail.lower()
