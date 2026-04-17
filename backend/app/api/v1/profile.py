"""
Profile Management API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import Optional
import os
import uuid

from app.db.database import get_db
from app.db import models
from app.schemas.auth_schemas import UserResponse
from app.core.dependencies import get_current_user
from app.core.config import settings

router = APIRouter()

# Avatar upload directory
AVATAR_DIR = os.path.join(settings.UPLOAD_DIR, "avatars")
os.makedirs(AVATAR_DIR, exist_ok=True)

MAX_AVATAR_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


@router.get("", response_model=UserResponse)
async def get_profile(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user profile"""
    return {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "avatar_url": current_user.avatar_url,
        "bio": current_user.bio,
        "phone_number": current_user.phone_number,
        "language": current_user.language,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else current_user.created_at.isoformat()
    }


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    phone_number: Optional[str] = None


@router.put("")
async def update_profile(
    profile_data: ProfileUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    user = current_user
    
    # Update only provided fields
    update_data = profile_data.model_dump(exclude_unset=True)
    
    # If email is being changed, check uniqueness
    if "email" in update_data and update_data["email"] != user.email:
        existing = db.query(models.User).filter(
            models.User.email == update_data["email"]
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered by another user",
            )
    
    for field, value in update_data.items():
        setattr(user, field, value)
    
    # Update timestamp
    user.updated_at = datetime.now(timezone.utc)
    
    db.commit()
    db.refresh(user)
    
  # ── NOTIFICATION: Profile Updated ────────────────────────────
    from app.core.events import event_dispatcher, EVENT_PROFILE_UPDATED
    event_dispatcher.dispatch(EVENT_PROFILE_UPDATED, {
        "db": db,
        "user_id": user.id,
    })
    db.commit()  # Commit notification


    return {
        "success": True,
        "message": "Profile updated",
        "profile": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "bio": user.bio,
            "phone_number": user.phone_number,
            "language": user.language,
            "created_at": user.created_at.isoformat(),
            "updated_at": user.updated_at.isoformat()
        }
    }


class LanguageUpdate(BaseModel):
    language: str = "en"


@router.put("/settings/language")
async def update_language(
    language_data: LanguageUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user language preference"""
    current_user.language = language_data.language
    db.commit()
    
    return {"success": True}


@router.put("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Upload profile avatar image.
    
    Accepts JPEG, PNG, WebP. Max 5MB.
    Returns the avatar URL path.
    """
    # Validate content type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image type: {file.content_type}. Allowed: JPEG, PNG, WebP",
        )
    
    # Read and validate size
    content = await file.read()
    if len(content) > MAX_AVATAR_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image too large ({len(content) / 1024 / 1024:.1f}MB). Max 5MB.",
        )
    
    # Delete old avatar if exists
    if current_user.avatar_url:
        old_filename = current_user.avatar_url.split("/")[-1]
        old_path = os.path.join(AVATAR_DIR, old_filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
    
    # Save new avatar
    ext = file.filename.rsplit(".", 1)[-1] if file.filename and "." in file.filename else "jpg"
    filename = f"{uuid.uuid4().hex}.{ext}"
    filepath = os.path.join(AVATAR_DIR, filename)
    
    with open(filepath, "wb") as f:
        f.write(content)
    
    # Update user avatar URL
    avatar_url = f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    current_user.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return {
        "success": True,
        "avatar_url": avatar_url,
    }
