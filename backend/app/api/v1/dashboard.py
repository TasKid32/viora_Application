"""
Dashboard API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.database import get_db
from app.db import models
from app.schemas.dashboard_schemas import DashboardResponse
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("")
async def get_dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get dashboard data for authenticated user.

    Progress is now REAL — based only on actual resource completion.
    No fake percentages for uploading CV or generating roadmap.
    """

    # Get user's latest analysis
    latest_analysis = db.query(models.SkillAnalysis).filter(
        models.SkillAnalysis.user_id == current_user.id,
        models.SkillAnalysis.is_archived.is_(False),
    ).order_by(models.SkillAnalysis.analyzed_at.desc()).first()

    # Get latest roadmap
    latest_roadmap = db.query(models.LearningRoadmap).filter(
        models.LearningRoadmap.user_id == current_user.id,
        models.LearningRoadmap.is_archived.is_(False),
    ).order_by(models.LearningRoadmap.created_at.desc()).first()

    # Count courses
    total_courses = db.query(models.Course).filter(
        models.Course.user_id == current_user.id
    ).count()
    completed_courses = db.query(models.Course).filter(
        models.Course.user_id == current_user.id,
        models.Course.completion == 100
    ).count()

    # ── Roadmap progress — handles BOTH old and new formats ──
    roadmap_total_steps = 0
    roadmap_completed_steps = 0
    roadmap_total_resources = 0
    roadmap_completed_resources = 0
    topics_total = 0
    topics_completed = 0

    if latest_roadmap and latest_roadmap.roadmap_data:
        roadmap_total_steps = len(latest_roadmap.roadmap_data)
        roadmap_completed_steps = sum(
            1 for step in latest_roadmap.roadmap_data
            if step.get("completed", False)
        )

        for step in latest_roadmap.roadmap_data:
            topics = step.get("topics", [])

            for topic in topics:
                if isinstance(topic, dict) and "resources" in topic:
                    # NEW format: per-topic resources
                    topic_resources = topic.get("resources", [])
                    topics_total += 1
                    topic_done = True
                    for r in topic_resources:
                        roadmap_total_resources += 1
                        if r.get("completed", False):
                            roadmap_completed_resources += 1
                        else:
                            topic_done = False
                    if topic_done and topic_resources:
                        topics_completed += 1
                # OLD format: string topics — fall through

            # OLD format: flat resources list
            for r in step.get("resources", []):
                roadmap_total_resources += 1
                if r.get("completed", False):
                    roadmap_completed_resources += 1

    # ── Real learning progress (0-100) ──
    # ONLY based on actual resource completion — no fake points
    learning_progress = 0
    if roadmap_total_resources > 0:
        learning_progress = int(
            (roadmap_completed_resources / roadmap_total_resources) * 100
        )

    # Journey step: where is the user in their journey?
    if latest_roadmap and roadmap_completed_resources > 0:
        journey_step = "learning"
    elif latest_roadmap:
        journey_step = "roadmap_ready"
    elif latest_analysis:
        journey_step = "analyzed"
    else:
        journey_step = "new"

    # Get unread notifications count
    notifications_count = db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read.is_(False)
    ).count()

    return {
        "user": {
            "id": current_user.id,
            "name": current_user.full_name,
            "email": current_user.email,
            "profile_picture": current_user.avatar_url,
            "created_at": current_user.created_at.isoformat(),
            "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else current_user.created_at.isoformat()
        },
        "progress": {
            "learning_progress": learning_progress,
            "journey_step": journey_step,
            "skills_found": len(latest_analysis.strong_skills or []) if latest_analysis else 0,
            "has_analysis": latest_analysis is not None,
            "has_roadmap": latest_roadmap is not None,
            "roadmap_steps_total": roadmap_total_steps,
            "roadmap_steps_completed": roadmap_completed_steps,
            "roadmap_resources_total": roadmap_total_resources,
            "roadmap_resources_completed": roadmap_completed_resources,
            "topics_total": topics_total,
            "topics_completed": topics_completed,
            "total_courses": total_courses,
            "completed_courses_count": completed_courses,
            # Legacy fields — backward compat
            "overall_percentage": learning_progress,
            "skill_growth": len(latest_analysis.strong_skills or []) if latest_analysis else 0,
        },
        "notifications_count": notifications_count
    }

