"""
Authentication Service — Business logic for user registration and login.

Extracted from route handlers to keep controllers thin.
"""
from datetime import timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.db import models
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def _build_user_response(user: models.User) -> dict:
    """Build a consistent user response dict from a User model."""
    return {
        "id": user.id,
        "full_name": user.full_name,
        "email": user.email,
        "avatar_url": user.avatar_url,
        "created_at": user.created_at.isoformat(),
        "updated_at": (
            user.updated_at.isoformat()
            if user.updated_at
            else user.created_at.isoformat()
        ),
    }


def _create_token_pair(user: models.User) -> dict:
    """Create access + refresh token pair for a user."""
    token_data = {"sub": user.email, "user_id": user.id}

    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    refresh_token = create_refresh_token(
        data=token_data,
        expires_delta=timedelta(days=7),
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": _build_user_response(user),
    }


def register_user(db: Session, full_name: str, email: str, password: str, confirm_password: str) -> dict:
    """Register a new user.

    Args:
        db: Database session.
        full_name: User's full name.
        email: User's email.
        password: User's password.
        confirm_password: Password confirmation.

    Returns:
        Dict with access_token, refresh_token, and user info.

    Raises:
        HTTPException: On validation failure or duplicate email.
    """
    # Validate passwords match
    if password != confirm_password:
        logger.warning("Registration failed: passwords do not match for %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match",
        )

    # Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == email).first()
    if existing_user:
        logger.warning("Registration failed: email already registered — %s", email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    hashed_password = get_password_hash(password)
    new_user = models.User(
        full_name=full_name,
        email=email,
        password_hash=hashed_password,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    logger.info("User registered successfully: id=%s email=%s", new_user.id, email)
    return _create_token_pair(new_user)

 # ── NOTIFICATION: Welcome new user ───────────────────────────
    from app.core.events import event_dispatcher, EVENT_USER_REGISTERED
    event_dispatcher.dispatch(EVENT_USER_REGISTERED, {
        "db": db,
        "user_id": new_user.id,
        "full_name": full_name,
    })
    db.commit()  # Commit notification



def login_user(db: Session, email: str, password: str) -> dict:
    """Authenticate a user and return tokens.

    Args:
        db: Database session.
        email: User's email.
        password: User's password.

    Returns:
        Dict with access_token, refresh_token, and user info.

    Raises:
        HTTPException: On invalid credentials.
    """
    user = db.query(models.User).filter(models.User.email == email).first()

    if not user or not verify_password(password, user.password_hash):
        logger.warning("Login failed: invalid credentials for %s", email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    logger.info("User logged in: id=%s email=%s", user.id, email)
    return _create_token_pair(user)
