"""
Authentication API Routes — Thin controllers delegating to AuthService.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import models
from app.schemas.auth_schemas import UserRegister, UserLogin
from app.services.auth_service import register_user, login_user
from app.core.security import (
    decode_token, create_access_token, create_refresh_token,
    get_password_hash, create_password_reset_token, verify_password_reset_token,
)
from app.core.config import settings
from app.core.logging import get_logger
from app.services.email_service import email_service
from datetime import timedelta

router = APIRouter()
logger = get_logger(__name__)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        return register_user(
            db=db,
            full_name=user_data.full_name,
            email=user_data.email,
            password=user_data.password,
            confirm_password=user_data.confirm_password,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during registration")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed" if not settings.DEBUG else f"Registration failed: {e}",
        )


@router.post("/login")
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT tokens."""
    try:
        return login_user(
            db=db,
            email=credentials.email,
            password=credentials.password,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error during login")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed" if not settings.DEBUG else f"Login failed: {e}",
        )


# ── B1 Fix: Token Refresh Endpoint ──────────────────────────────

class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/refresh")
async def refresh_token(body: RefreshRequest, db: Session = Depends(get_db)):
    """Refresh an expired access token using a valid refresh token."""
    payload = decode_token(body.refresh_token, expected_type="refresh")

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    user_id = payload.get("user_id")
    email = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    # Verify user still exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Create new token pair
    token_data = {"sub": email, "user_id": user_id}
    new_access = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    new_refresh = create_refresh_token(
        data=token_data,
        expires_delta=timedelta(days=7),
    )

    logger.info("Token refreshed for user: %s", user_id)
    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
    }


# ── B2 Fix: Forgot Password Endpoint ────────────────────────────

class ForgotPasswordRequest(BaseModel):
    email: EmailStr


@router.post("/forgot-password")
async def forgot_password(body: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request a password reset link.

    Generates a time-limited token (via itsdangerous) and sends it via SMTP.
    For security, always returns success to avoid email enumeration attacks.
    """
    user = db.query(models.User).filter(models.User.email == body.email).first()

    if user:
        # Generate secure time-limited token
        token = create_password_reset_token(body.email)

        # Send reset email via SMTP
        sent = email_service.send_password_reset(body.email, token)
        if sent:
            logger.info("Password reset email sent to: %s", body.email)
        else:
            logger.warning("Password reset email could not be sent to: %s", body.email)
    else:
        logger.info("Password reset requested for non-existent email: %s", body.email)

    # Always return success (prevent email enumeration)
    return {
        "success": True,
        "message": "If this email is registered, a password reset link will be sent.",
    }


# ── B2 Fix: Reset Password Endpoint ─────────────────────────────

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str
    confirm_password: str

    @field_validator("new_password")
    @classmethod
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v

    @field_validator("confirm_password")
    @classmethod
    def passwords_match(cls, v, info):
        if "new_password" in info.data and v != info.data["new_password"]:
            raise ValueError("Passwords do not match")
        return v


@router.post("/reset-password")
async def reset_password(body: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using a valid token from the reset email.

    Verifies the itsdangerous token, updates the password, and
    sends a confirmation notification email.
    """
    # Verify token
    email = verify_password_reset_token(body.token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token",
        )

    # Find user
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update password
    user.password = get_password_hash(body.new_password)
    db.commit()

    # Send confirmation notification (security best practice)
    email_service.send_password_changed_notification(email)

    logger.info("Password reset completed for: %s", email)
    return {
        "success": True,
        "message": "Password has been reset successfully.",
    }

