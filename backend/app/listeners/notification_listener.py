from typing import Dict, Any
from app.core.events import (
    EventDispatcher,
    EVENT_USER_REGISTERED,
    EVENT_CV_ANALYSIS_COMPLETED,
    EVENT_ROADMAP_GENERATED,
    EVENT_ROADMAP_PHASE_COMPLETED,
    EVENT_COURSE_COMPLETED,
    EVENT_PROFILE_UPDATED,
)
from app.services.notification_service import get_notification_service

def on_user_registered(payload: Dict[str, Any]):
    db = payload.get("db")
    user_id = payload.get("user_id")
    full_name = payload.get("full_name")
    if db and user_id and full_name:
        get_notification_service().notify_welcome(db, user_id, full_name)

def on_cv_analysis_completed(payload: Dict[str, Any]):
    db = payload.get("db")
    user_id = payload.get("user_id")
    job_title = payload.get("job_title")
    skills_found = payload.get("skills_found")
    gaps_found = payload.get("gaps_found")
    if db and user_id:
        get_notification_service().notify_cv_analysis_completed(
            db, user_id, job_title, skills_found, gaps_found
        )

def on_roadmap_generated(payload: Dict[str, Any]):
    db = payload.get("db")
    user_id = payload.get("user_id")
    phase_count = payload.get("phase_count")
    total_topics = payload.get("total_topics")
    if db and user_id:
        get_notification_service().notify_roadmap_generated(
            db, user_id, phase_count, total_topics
        )

def on_roadmap_phase_completed(payload: Dict[str, Any]):
    db = payload.get("db")
    user_id = payload.get("user_id")
    phase_name = payload.get("phase_name")
    if db and user_id:
        get_notification_service().notify_roadmap_phase_completed(
            db, user_id, phase_name
        )

def on_course_completed(payload: Dict[str, Any]):
    db = payload.get("db")
    user_id = payload.get("user_id")
    course_title = payload.get("course_title")
    if db and user_id:
        get_notification_service().notify_course_completed(
            db, user_id, course_title
        )

def on_profile_updated(payload: Dict[str, Any]):
    db = payload.get("db")
    user_id = payload.get("user_id")
    if db and user_id:
        get_notification_service().notify_profile_updated(db, user_id)


def setup_notification_listeners(dispatcher: EventDispatcher):
    """Register all notification listeners to the event dispatcher."""
    dispatcher.register(EVENT_USER_REGISTERED, on_user_registered)
    dispatcher.register(EVENT_CV_ANALYSIS_COMPLETED, on_cv_analysis_completed)
    dispatcher.register(EVENT_ROADMAP_GENERATED, on_roadmap_generated)
    dispatcher.register(EVENT_ROADMAP_PHASE_COMPLETED, on_roadmap_phase_completed)
    dispatcher.register(EVENT_COURSE_COMPLETED, on_course_completed)
    dispatcher.register(EVENT_PROFILE_UPDATED, on_profile_updated)