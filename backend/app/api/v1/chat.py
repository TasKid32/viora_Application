"""
AI Chat Assistant API Routes
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.db.database import get_db
from app.db import models
from app.schemas.chat_schemas import ChatMessage, ChatResponse
from app.core.dependencies import get_current_user

from app.services.llm_service import llm_service

router = APIRouter()


@router.post("/send", response_model=ChatResponse)
async def send_message(
    chat_data: ChatMessage,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Send message to AI assistant"""
    
    # Get user context (latest analysis)
    user_id = current_user.id
    context = None
    analysis = db.query(models.SkillAnalysis).filter(
        models.SkillAnalysis.user_id == user_id,
        models.SkillAnalysis.is_archived.is_(False),
    ).order_by(models.SkillAnalysis.analyzed_at.desc()).first()
    
    if analysis:
        skills_list = analysis.strong_skills or []
        entities = analysis.extracted_entities or {}
        context = {
            "job_title": analysis.predicted_job_title,
            "experience_level": analysis.experience_level,
            "skills": [
                s["name"] for s in skills_list
                if isinstance(s, dict) and "name" in s
            ],
            "missing_skills": analysis.missing_skills or [],
        }
        # Add roadmap progress if available
        roadmap = db.query(models.LearningRoadmap).filter(
            models.LearningRoadmap.user_id == user_id,
            models.LearningRoadmap.is_archived.is_(False),
        ).order_by(models.LearningRoadmap.created_at.desc()).first()
        if roadmap:
            phases = roadmap.roadmap_data or []
            total_steps = sum(len(p.get("topics", [])) for p in phases)
            completed = sum(
                1 for p in phases
                for t in p.get("topics", [])
                if isinstance(t, dict) and t.get("completed")
            )
            context["roadmap_progress"] = f"{completed}/{total_steps} steps completed"
    
    # Get LLM response
    reply = await llm_service.chat_assistant(
        user_message=chat_data.message,
        context=context
    )
    
    # Build smart bilingual suggestions based on user state + language
    # Detect language BEFORE try — so catch block can use it safely
    arabic_chars = sum(1 for c in chat_data.message if '\u0600' <= c <= '\u06FF')
    is_arabic = arabic_chars > len(chat_data.message) * 0.3

    try:

        if not analysis:
            if is_arabic:
                suggestions = [
                    "حلل سيرتي الذاتية",
                    "ما المهارات المطلوبة في سوق العمل؟",
                    "نصائح لتحسين CV",
                ]
            else:
                suggestions = [
                    "Analyze my CV",
                    "What skills are in demand?",
                    "Tips to improve my CV",
                ]
        else:
            first_missing = (
                analysis.missing_skills[0]
                if analysis.missing_skills
                else None
            )
            job = analysis.predicted_job_title or ('مهني' if is_arabic else 'career')
            suggestions = []
            if first_missing:
                if is_arabic:
                    suggestions.append(f"كيف أتعلم {first_missing}؟")
                else:
                    suggestions.append(f"How to learn {first_missing}?")
            if is_arabic:
                suggestions.append(f"نصائح لمسار {job}")
                suggestions.append("أنشئ خارطة تعلم")
            else:
                suggestions.append(f"Tips for {job} career")
                suggestions.append("Create learning roadmap")
    except (TypeError, IndexError, KeyError):
        if is_arabic:
            suggestions = ["حلل سيرتي الذاتية", "نصائح مهنية", "أنشئ خارطة تعلم"]
        else:
            suggestions = ["Analyze my CV", "Career advice", "Create learning roadmap"]
    
    # Save chat history
    chat_record = models.ChatHistory(
        user_id=user_id,
        message=chat_data.message,
        reply=reply
    )
    
    db.add(chat_record)
    db.commit()
    
    return {
        "reply": reply,
        "suggestions": suggestions,
        "timestamp": datetime.now(timezone.utc)
    }


@router.get("/history")
async def get_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get chat history for user"""
    
    chats = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).order_by(models.ChatHistory.timestamp.desc()).limit(50).all()
    
    return {
        "chats": [
            {
                "message": chat.message,
                "reply": chat.reply,
                "timestamp": chat.timestamp
            }
            for chat in chats
        ]
    }


@router.delete("/history")
async def clear_chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Clear all chat history for user.
    
    Called automatically when user re-analyzes their CV,
    so the assistant focuses on the new analysis context.
    """
    deleted = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == current_user.id
    ).delete()
    db.commit()
    
    return {"deleted_count": deleted}
