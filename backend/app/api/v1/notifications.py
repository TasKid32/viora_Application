"""
Notifications API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.db.database import get_db
from app.db import models
from app.schemas.notification_schemas import NotificationResponse
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("", response_model=dict)
async def get_notifications(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for user"""
    
    unread_count = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read.is_(False)
    ).count()
    
    notifications = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id
    ).order_by(models.Notification.created_at.desc()).all()
    
    notification_list = []
    for n in notifications:
        icon_map = {
            "cv_analysis": "✅",
            "achievement": "🏆",
            "course_recommendation": "📚",
            "progress_report": "📊"
        }
        
        # Return ISO timestamp — let the client format it
        ts = n.created_at
        if ts and ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        
        notification_list.append({
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "message": n.message,
            "timestamp": ts.isoformat() if ts else None,
            "is_read": n.is_read,
            "icon": icon_map.get(n.type, "🔔")
        })
    
    return {
        "unread_count": unread_count,
        "notifications": notification_list
    }


@router.put("/{notification_id}/read")
async def mark_as_read(
    notification_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark notification as read"""
    
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    notification.is_read = True
    db.commit()
    
    return {"success": True}


@router.delete("/{notification_id}")
async def delete_notification(
    notification_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete notification"""
    
    notification = db.query(models.Notification).filter(
        models.Notification.id == notification_id,
        models.Notification.user_id == current_user.id
    ).first()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    db.delete(notification)
    db.commit()
    
    return {"success": True}


@router.put("/read-all")
async def mark_all_as_read(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark ALL notifications as read in a single batch operation."""
    
    updated = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read.is_(False)
    ).update({"is_read": True})
    
    db.commit()
    
    return {"success": True, "marked_count": updated}
