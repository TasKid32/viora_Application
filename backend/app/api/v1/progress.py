"""
Progress Tracking API Routes — Real DB queries.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta, timezone

from app.db.database import get_db
from app.db import models
from app.schemas.progress_schemas import WeeklyActivity, CompletedCourse
from app.core.dependencies import get_current_user

router = APIRouter()


@router.get("/weekly", response_model=WeeklyActivity)
async def get_weekly_activity(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly activity stats from real user data.

    B3 Fix: Counts course completions and chat interactions per day
    over the past 7 days instead of returning zeros.
    """
    now = datetime.now(timezone.utc)
    week_start = now - timedelta(days=6)  # Last 7 days

    # Map: weekday index (0=Mon) -> day name
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    activity = {d: 0 for d in day_names}

    # Count chat messages per day
    chats = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id,
        models.ChatHistory.timestamp >= week_start,
    ).all()

    for chat in chats:
        if chat.timestamp:
            ts = chat.timestamp
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            day_key = day_names[ts.weekday()]
            activity[day_key] += 1

    # Count course updates per day
    courses = db.query(models.Course).filter(
        models.Course.user_id == current_user.id,
        models.Course.updated_at >= week_start,
    ).all()

    for course in courses:
        if course.updated_at:
            ts = course.updated_at
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            day_key = day_names[ts.weekday()]
            activity[day_key] += 1

    return activity


@router.get("/courses", response_model=List[CompletedCourse])
async def get_completed_courses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get completed courses from database."""
    courses = db.query(models.Course).filter(
        models.Course.user_id == current_user.id,
        models.Course.completion == 100
    ).all()

    return [
        {
            "title": c.title,
            "category": c.category,
            "completion": c.completion,
        }
        for c in courses
    ]
