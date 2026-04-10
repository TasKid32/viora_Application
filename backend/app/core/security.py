"""
Authentication utilities - Password hashing and JWT tokens.

Uses timezone-aware datetimes (Python 3.11+ compatible).
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
import bcrypt

from app.core.config import settings


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"),
        hashed_password.encode("utf-8"),
    )


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt.

    Truncates to 72 bytes per bcrypt specification.
    """
    password_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def create_access_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token with timezone-aware expiry."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire, "token_type": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(
    data: dict, expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT refresh token (longer-lived, different token_type)."""
    to_encode = data.copy()
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(days=7)

    to_encode.update({"exp": expire, "token_type": "refresh"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str, expected_type: str = "access") -> Optional[dict]:
    """Decode and verify a JWT token.

    Args:
        token: The JWT token string.
        expected_type: Expected token_type claim ("access" or "refresh").

    Returns:
        Token payload dict, or None if invalid/expired/wrong type.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Validate token type to prevent using refresh as access or vice versa
        if payload.get("token_type") != expected_type:
            return None
        return payload
    except JWTError:
        return None


# ── Password Reset Tokens ─────────────────────────────────────
# Uses itsdangerous for URL-safe, time-limited tokens (separate from JWT)

from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


def create_password_reset_token(email: str) -> str:
    """Generate a time-limited password reset token.

    Token embeds the email and is signed with SECRET_KEY.
    Uses a separate 'salt' to prevent token reuse across different contexts.
    """
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    return serializer.dumps(email, salt="password-reset-salt")


def verify_password_reset_token(token: str) -> Optional[str]:
    """Verify a password reset token.

    Args:
        token: The URL-safe token from the reset link.

    Returns:
        The email address if valid, None if expired or tampered.
    """
    max_age = getattr(settings, "PASSWORD_RESET_EXPIRE_MINUTES", 30) * 60
    serializer = URLSafeTimedSerializer(settings.SECRET_KEY)
    try:
        email = serializer.loads(token, salt="password-reset-salt", max_age=max_age)
        return email
    except (SignatureExpired, BadSignature):
        return None
