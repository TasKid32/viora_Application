"""
Notification Service — Real event-driven notification system.

This service is called from business logic layers (services) to create
notifications when real user-impacting events occur.

NO fake data. NO UI-only notifications. ONLY real backend events.
"""
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime, timezone

from app.db import models
from app.core.logging import get_logger

logger = get_logger(__name__)


class NotificationService:
    """
    Centralized notification creation service.
    
    All notifications MUST originate from real business events:
    - CV analysis completed
    - Roadmap generated
    - Course completed
    - Profile updated
    - Achievement unlocked
    - System jobs completed
    """

    @staticmethod
    def create_notification(
        db: Session,
        user_id: str,
        title: str,
        message: str,
        notification_type: str,
    ) -> models.Notification:
        """
        Create a new notification in the database.
        
        Args:
            db: Database session
            user_id: Target user ID
            title: Notification title
            message: Notification message body
            notification_type: Type of notification (cv_analysis, roadmap, course, etc.)
            
        Returns:
            Created Notification model instance
        """
        notification = models.Notification(
            user_id=user_id,
            type=notification_type,
            title=title,
            message=message,
            is_read=False,
        )
        
        db.add(notification)
        db.flush()  # Get ID without committing transaction
        
        logger.info(
            "Notification created: id=%s, user=%s, type=%s, title=%s",
            notification.id, user_id, notification_type, title
        )
        
        return notification

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: str,
        limit: Optional[int] = None,
        unread_only: bool = False,
    ) -> List[models.Notification]:
        """Get notifications for a user."""
        query = db.query(models.Notification).filter(
            models.Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(models.Notification.is_read.is_(False))
        
        query = query.order_by(models.Notification.created_at.desc())
        
        if limit:
            query = query.limit(limit)
        
        return query.all()

    @staticmethod
    def get_unread_count(db: Session, user_id: str) -> int:
        """Get count of unread notifications for a user."""
        return db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.is_read.is_(False)
        ).count()

    @staticmethod
    def mark_as_read(
        db: Session,
        notification_id: str,
        user_id: str,
    ) -> bool:
        """Mark a notification as read."""
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        db.flush()
        
        logger.info("Notification marked as read: id=%s", notification_id)
        return True

    @staticmethod
    def mark_all_as_read(db: Session, user_id: str) -> int:
        """Mark all notifications as read for a user."""
        updated = db.query(models.Notification).filter(
            models.Notification.user_id == user_id,
            models.Notification.is_read.is_(False)
        ).update({"is_read": True})
        
        db.flush()
        
        logger.info("Marked %d notifications as read for user: %s", updated, user_id)
        return updated

    @staticmethod
    def delete_notification(
        db: Session,
        notification_id: str,
        user_id: str,
    ) -> bool:
        """Delete a notification."""
        notification = db.query(models.Notification).filter(
            models.Notification.id == notification_id,
            models.Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        db.delete(notification)
        db.flush()
        
        logger.info("Notification deleted: id=%s", notification_id)
        return True

   # ── Event-specific notification creators ──────────────────────

    @staticmethod
    def notify_cv_analysis_completed(
        db: Session,
        user_id: str,
        job_title: str,
        skills_found: int,
        gaps_found: int,
    ) -> models.Notification:
        """Notify user that CV analysis is complete."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="CV Analysis Completed",
            message=f"Your CV has been analyzed! Predicted role: {job_title}. "
                   f"Found {skills_found} skills and identified {gaps_found} skill gaps.",
            notification_type="cv_analysis",
        )

    @staticmethod
    def notify_roadmap_generated(
        db: Session,
        user_id: str,
        phase_count: int,
        total_topics: int,
    ) -> models.Notification:
        """Notify user that learning roadmap has been generated."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Learning Roadmap Ready",
            message=f"Your personalized learning roadmap is ready! "
                   f"{phase_count} phases with {total_topics} topics to master.",
            notification_type="roadmap",
        )

    @staticmethod
    def notify_course_completed(
        db: Session,
        user_id: str,
        course_title: str,
    ) -> models.Notification:
        """Notify user that they completed a course."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Course Completed! 🎉",
            message=f"Congratulations! You've completed '{course_title}'. "
                   f"Keep up the great work!",
            notification_type="achievement",
        )

    @staticmethod
    def notify_profile_updated(
        db: Session,
        user_id: str,
    ) -> models.Notification:
        """Notify user that their profile was updated."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Profile Updated",
            message="Your profile information has been successfully updated.",
            notification_type="system",
        )

    @staticmethod
    def notify_roadmap_phase_completed(
        db: Session,
        user_id: str,
        phase_name: str,
    ) -> models.Notification:
        """Notify user that they completed a roadmap phase."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Phase Completed! 🏆",
            message=f"Great progress! You've completed the '{phase_name}' phase. "
                   f"Ready for the next challenge?",
            notification_type="achievement",
        )

    @staticmethod
    def notify_welcome(
        db: Session,
        user_id: str,
        full_name: str,
    ) -> models.Notification:
        """Welcome notification for new users."""
        return NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title=f"Welcome to Viora, {full_name}!",
            message="Start your career journey by uploading your CV for personalized analysis.",
            notification_type="system",
        )


# ── Singleton instance ──────────────────────────────────────────

_notification_service: Optional[NotificationService] = None


def get_notification_service() -> NotificationService:
    """Get notification service singleton."""
    global _notification_service
    if _notification_service is None:
        _notification_service = NotificationService()
    return _notification_service