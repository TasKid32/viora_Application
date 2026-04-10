"""
Course Management API Routes.

Uses course_to_dict() helper to eliminate response-building duplication.
Uses timezone-aware datetimes.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timezone

from app.db.database import get_db
from app.db import models
from app.schemas.course_schemas import CourseResponse, CourseCreate, CourseUpdate
from app.core.dependencies import get_current_user

router = APIRouter()


def course_to_dict(course: models.Course) -> dict:
    """Convert a Course model to a response dict.

    Extracted to eliminate duplication — was repeated 6 times.
    """
    return {
        "id": course.id,
        "title": course.title,
        "category": course.category,
        "platform": course.platform,
        "completion": course.completion,
        "enrolled_date": course.enrolled_date.isoformat() if course.enrolled_date else None,
        "completed_date": course.completed_date.isoformat() if course.completed_date else None,
    }


@router.get("", response_model=List[CourseResponse])
async def get_courses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all courses for user."""
    courses = (
        db.query(models.Course)
        .filter(models.Course.user_id == current_user.id)
        .order_by(models.Course.created_at.desc())
        .all()
    )
    return [course_to_dict(c) for c in courses]


@router.get("/completed", response_model=List[CourseResponse])
async def get_completed_courses(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get completed courses for user."""
    courses = (
        db.query(models.Course)
        .filter(
            models.Course.user_id == current_user.id,
            models.Course.completion == 100,
        )
        .order_by(models.Course.completed_date.desc())
        .all()
    )
    return [course_to_dict(c) for c in courses]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get specific course."""
    course = (
        db.query(models.Course)
        .filter(
            models.Course.id == course_id,
            models.Course.user_id == current_user.id,
        )
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    return course_to_dict(course)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course_data: CourseCreate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create new course."""
    course = models.Course(
        user_id=current_user.id,
        title=course_data.title,
        category=course_data.category,
        platform=course_data.platform,
        completion=course_data.completion,
        enrolled_date=datetime.now(timezone.utc),
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course_to_dict(course)


@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update course."""
    course = (
        db.query(models.Course)
        .filter(
            models.Course.id == course_id,
            models.Course.user_id == current_user.id,
        )
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    # Update fields
    if course_data.title is not None:
        course.title = course_data.title
    if course_data.category is not None:
        course.category = course_data.category
    if course_data.platform is not None:
        course.platform = course_data.platform
    if course_data.completion is not None:
        course.completion = course_data.completion
        if course_data.completion == 100 and course.completed_date is None:
            course.completed_date = datetime.now(timezone.utc)
    if course_data.completed_date is not None:
        course.completed_date = datetime.fromisoformat(course_data.completed_date)

    db.commit()
    db.refresh(course)

    return course_to_dict(course)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: str,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete course."""
    course = (
        db.query(models.Course)
        .filter(
            models.Course.id == course_id,
            models.Course.user_id == current_user.id,
        )
        .first()
    )

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    db.delete(course)
    db.commit()

    return None
