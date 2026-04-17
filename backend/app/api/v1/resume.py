"""
Resume Analysis API Routes — Viora NER + O*NET Pipeline

Architecture (per REST best practices):
- Every /analyze call runs a FRESH pipeline (NER + O*NET ~200ms local).
- No stale cache — the pipeline is local ONNX, not an expensive API call.
- Old analyses are archived (soft-delete) to preserve history.
- pipeline_version tracks which code generated each result.
- Dashboard/GET endpoints read from DB (the real "cache").

Why no request-level cache?
  The old cache returned stale results for the same resume_id, hiding
  pipeline bugs and preventing verification of fixes. Since the pipeline
  runs locally in ~200ms (not calling Gemini/OpenAI), the cache provided
  negligible performance benefit while causing catastrophic correctness
  issues. Per REST best practice: POST endpoints should NOT be cached
  unless explicitly designed with idempotency keys and TTL — which does
  not apply to mutable analysis pipelines under active development.
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
import json
import os
import hashlib
from datetime import datetime

from app.db.database import get_db
from app.db import models
from app.schemas.resume_schemas import ResumeUploadResponse, SkillsInput, AnalysisRequest, AnalysisResponse
from app.services.file_upload import save_upload_file
from app.services.text_extractor import extract_text_from_file
from app.services.cv_quality import assess_cv_quality
from app.services.hybrid_analysis_service import get_hybrid_service
from app.services.onet_service import get_onet_service
from app.core.config import settings
from app.core.dependencies import get_current_user
from app.core.logging import get_logger

logger = get_logger(__name__)

# ── Pipeline version — increment after EVERY pipeline change ─────
# This is stamped into every analysis result so we can:
# 1. Identify which pipeline version produced each result
# 2. Debug whether a fix actually took effect
# 3. The mobile app can optionally show "Analyzed with Pipeline v3"
PIPELINE_VERSION = "3.2.0"


def detect_language(text: str) -> str:
    """Simple language detection"""
    arabic_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
    return "ar" if arabic_chars > len(text) * 0.3 else "en"


def _compute_text_hash(text: str) -> str:
    """Compute SHA-256 hash of extracted text for change detection."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _archive_old_analyses(db: Session, user_id: str) -> int:
    """Archive all active analyses + roadmaps + chats for a user.

    Returns number of archived analyses.
    Centralizes cleanup logic used by both /analyze and /analyze/stream.
    """
    old_analyses = db.query(models.SkillAnalysis).filter(
        models.SkillAnalysis.user_id == user_id,
        models.SkillAnalysis.is_archived.is_(False),
    ).all()

    if not old_analyses:
        return 0

    old_analysis_ids = [a.id for a in old_analyses]

    # Archive old roadmaps linked to old analyses
    archived_roadmaps = db.query(models.LearningRoadmap).filter(
        models.LearningRoadmap.analysis_id.in_(old_analysis_ids)
    ).update({models.LearningRoadmap.is_archived: True}, synchronize_session="fetch")

    # Archive old analyses
    for old in old_analyses:
        old.is_archived = True

    # Clear chat history so assistant focuses on new CV context
    deleted_chats = db.query(models.ChatHistory).filter(
        models.ChatHistory.user_id == user_id
    ).delete()

    db.flush()
    logger.info(
        "Re-analysis: archived %d roadmaps, %d analyses, cleared %d chats for user %s",
        archived_roadmaps, len(old_analyses), deleted_chats, user_id,
    )
    return len(old_analyses)


def _run_analysis_pipeline(entities: dict, request_additional_skills: list | None, quality: dict):
    """Build the analysis result dict from pipeline entities.

    Centralizes result-building logic used by both /analyze and /analyze/stream.
    Returns (all_skills, strong_skills, missing_hard, missing_soft).
    """
    # Merge additional skills if provided
    all_skills = list(set(entities.get("hard_skills", [])))
    if request_additional_skills:
        all_skills.extend(request_additional_skills)
        all_skills = list(set(all_skills))

    # Build strong_skills
    strong_skills = entities.get("strong_skills", [])
    if request_additional_skills:
        existing_skill_names = [s["name"] for s in strong_skills]
        for skill in request_additional_skills:
            if skill not in existing_skill_names:
                strong_skills.append({"name": skill, "proficiency": 70})

    # Gap analysis
    missing_hard = [item["skill"] for item in entities.get("missing_hard_skills", [])]
    missing_soft = [item["skill"] for item in entities.get("missing_soft_skills", [])]

    return all_skills, strong_skills, missing_hard, missing_soft


def _build_response(analysis, entities, all_skills, strong_skills, missing_hard, missing_soft, quality):
    """Build the final API response dict.

    Centralizes response-building logic used by both endpoints.
    """
    return {
        "analysis_id": analysis.id,
        "user_profile": {
            "predicted_job_title": analysis.predicted_job_title,
            "career_direction": entities.get("career_direction", ""),
            "extracted_skills": all_skills,
            "experience_level": analysis.experience_level,
            "strong_skills": strong_skills,
        },
        "job_opportunities": entities.get("job_opportunities", []),
        "gap_analysis": {
            "predicted_job": analysis.predicted_job_title,
            "experience_level": analysis.experience_level,
            "missing_hard_skills": missing_hard,
            "missing_soft_skills": missing_soft,
            "missing_skills": entities.get("missing_skills", []),
            "missing_tech_skills": entities.get("missing_tech_skills", []),
        },
        "recommendations": entities.get("recommendations", []),
        "languages": entities.get("languages", []),
        "cv_quality": quality,
        "processed_at": analysis.analyzed_at,
    }


router = APIRouter()


@router.post("/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload resume file (PDF/DOCX)"""

    # Validate file type
    allowed_extensions = [".pdf", ".doc", ".docx"]
    file_ext = os.path.splitext(file.filename)[1].lower()

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(allowed_extensions)}"
        )

    # Validate file size (max 10MB) — defense-in-depth with mobile check
    max_size = 10 * 1024 * 1024  # 10MB
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large ({len(content) / 1024 / 1024:.1f}MB). Maximum size is 10MB."
        )
    # Reset file position for saving
    await file.seek(0)

    # Save file
    file_path = await save_upload_file(file)

    # Create resume record
    new_resume = models.Resume(
        user_id=current_user.id,
        file_path=file_path,
        original_filename=file.filename,
        language="en"  # Will be detected later
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "file_id": new_resume.id,
        "filename": file.filename,
        "size": os.path.getsize(file_path),
        "uploaded_at": new_resume.uploaded_at
    }


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_resume(
    request: AnalysisRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze uploaded resume — ALWAYS runs fresh pipeline.

    Why no cache?
    - Pipeline runs locally via ONNX (~200ms) — no expensive API calls.
    - Stale cache hid pipeline bugs and prevented fix verification.
    - Per REST best practice: POST endpoints performing mutations
      should not silently return cached results.
    - Dashboard/GET endpoints read from DB, which IS the persistent store.
    """

    user_id = current_user.id

    # Get resume
    resume = db.query(models.Resume).filter(
        models.Resume.id == request.file_id,
        models.Resume.user_id == user_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    # ── Archive old analyses BEFORE new analysis ─────────────────
    _archive_old_analyses(db, user_id)

    # Extract text from file
    try:
        text = extract_text_from_file(resume.file_path)
    except (ValueError, HTTPException) as e:
        detail = e.detail if hasattr(e, 'detail') else str(e)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Could not extract text from resume: {detail}",
        )

    # Assess CV quality before proceeding
    quality = assess_cv_quality(text)
    if not quality["is_valid"]:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "The uploaded file does not appear to be a valid CV. "
                f"Quality score: {quality['quality_score']}/100. "
                + " ".join(quality["warnings"])
            ),
        )

    # Detect language
    language = detect_language(text)
    resume.language = language
    db.commit()

    # Reject Arabic CVs — NER model is English-only
    if language == "ar":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=(
                "Arabic CVs are not supported yet. "
                "Please upload an English CV for accurate analysis."
            ),
        )

    # ── Run FRESH pipeline: Viora NER (ONNX) + O*NET taxonomy ────
    logger.info(
        "Running fresh analysis pipeline v%s for user %s (resume %s)",
        PIPELINE_VERSION, user_id, resume.id,
    )
    hybrid = get_hybrid_service()
    entities = await hybrid.analyze_cv(text)

    # Build analysis results
    all_skills, strong_skills, missing_hard, missing_soft = _run_analysis_pipeline(
        entities, request.additional_skills, quality,
    )

    # Compute content hash for debugging/tracking
    text_hash = _compute_text_hash(text)

    # Create analysis record
    analysis = models.SkillAnalysis(
        user_id=user_id,
        resume_id=resume.id,
        predicted_job_title=entities.get("predicted_job", "Software Engineer"),
        experience_level=entities.get("experience_level", "Mid-Level"),
        strong_skills=strong_skills,
        missing_skills=missing_hard + missing_soft,
        extracted_entities={
            **entities,
            "additional_skills": request.additional_skills or [],
            "merged_skills": all_skills,
            "cv_quality": quality,
            "pipeline_version": PIPELINE_VERSION,
            "content_hash": text_hash,
        }
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    logger.info(
        "Analysis complete: id=%s, pipeline=v%s, hash=%s, skills=%d, gaps=%d",
        analysis.id, PIPELINE_VERSION, text_hash,
        len(all_skills), len(missing_hard) + len(missing_soft),
    )

 # ── NOTIFICATION: CV Analysis Completed ──────────────────────
    from app.core.events import event_dispatcher, EVENT_CV_ANALYSIS_COMPLETED
    event_dispatcher.dispatch(EVENT_CV_ANALYSIS_COMPLETED, {
        "db": db,
        "user_id": user_id,
        "job_title": analysis.predicted_job_title,
        "skills_found": len(all_skills),
        "gaps_found": len(missing_hard) + len(missing_soft),
    })
    db.commit()  # Commit notification


    # B5 Fix: Delete the uploaded file after successful analysis
    try:
        if resume.file_path and os.path.exists(resume.file_path):
            os.remove(resume.file_path)
            resume.file_path = None
            db.commit()
    except OSError as cleanup_err:
        logger.warning("Failed to clean up uploaded file %s: %s", resume.file_path, cleanup_err)

    # Build response
    result = _build_response(
        analysis, entities, all_skills, strong_skills,
        missing_hard, missing_soft, quality,
    )

    # Return with pipeline metadata headers for debugging
    response = JSONResponse(content=json.loads(json.dumps(result, default=str)))
    response.headers["X-Pipeline-Version"] = PIPELINE_VERSION
    response.headers["X-Content-Hash"] = text_hash
    response.headers["X-Cache-Status"] = "MISS"  # Always fresh — no cache
    return response


@router.post("/analyze/stream")
async def analyze_resume_stream(
    request: AnalysisRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """SSE streaming endpoint — sends real-time analysis stage events.

    ALWAYS runs fresh pipeline (same as /analyze — no stale cache).

    Events:
      event: stage  data: {"step": "extracting_text"}
      event: stage  data: {"step": "running_ner"}
      event: stage  data: {"step": "matching_onet"}
      event: result data: { ... full analysis result ... }
    """
    user_id = current_user.id
    resume = db.query(models.Resume).filter(
        models.Resume.id == request.file_id,
        models.Resume.user_id == user_id
    ).first()

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    async def event_generator():
        """Async generator that yields SSE events as analysis progresses."""
        try:
            # Stage 1: Extract text
            yield f"event: stage\ndata: {json.dumps({'step': 'extracting_text'})}\n\n"

            text = extract_text_from_file(resume.file_path)
            quality = assess_cv_quality(text)
            if not quality["is_valid"]:
                error_msg = (
                    "The uploaded file does not appear to be a valid CV. "
                    f"Quality score: {quality['quality_score']}/100."
                )
                yield f"event: error\ndata: {json.dumps({'detail': error_msg})}\n\n"
                return

            # Stage 2: NER analysis — ALWAYS fresh
            yield f"event: stage\ndata: {json.dumps({'step': 'running_ner'})}\n\n"

            logger.info(
                "SSE: Running fresh pipeline v%s for user %s",
                PIPELINE_VERSION, user_id,
            )
            hybrid = get_hybrid_service()
            entities = await hybrid.analyze_cv(text)

            # Stage 3: O*NET matching
            yield f"event: stage\ndata: {json.dumps({'step': 'matching_onet'})}\n\n"

            # Build analysis results
            all_skills, strong_skills, missing_hard, missing_soft = _run_analysis_pipeline(
                entities, request.additional_skills, quality,
            )

            # Archive old analyses
            _archive_old_analyses(db, user_id)

            # Compute content hash
            text_hash = _compute_text_hash(text)

            # Save analysis
            analysis = models.SkillAnalysis(
                user_id=user_id,
                resume_id=resume.id,
                predicted_job_title=entities.get("predicted_job", "Software Engineer"),
                experience_level=entities.get("experience_level", "Mid-Level"),
                strong_skills=strong_skills,
                missing_skills=missing_hard + missing_soft,
                extracted_entities={
                    **entities,
                    "additional_skills": request.additional_skills or [],
                    "merged_skills": all_skills,
                    "cv_quality": quality,
                    "pipeline_version": PIPELINE_VERSION,
                    "content_hash": text_hash,
                }
            )
            db.add(analysis)
            db.commit()
            db.refresh(analysis)

            logger.info(
                "SSE analysis complete: id=%s, pipeline=v%s, hash=%s",
                analysis.id, PIPELINE_VERSION, text_hash,
            )


 # ── NOTIFICATION: CV Analysis Completed ──────────────────────
            from app.core.events import event_dispatcher, EVENT_CV_ANALYSIS_COMPLETED
            event_dispatcher.dispatch(EVENT_CV_ANALYSIS_COMPLETED, {
                "db": db,
                "user_id": user_id,
                "job_title": analysis.predicted_job_title,
                "skills_found": len(all_skills),
                "gaps_found": len(missing_hard) + len(missing_soft),
            })
            db.commit()  # Commit notification

            # Cleanup file
            try:
                if resume.file_path and os.path.exists(resume.file_path):
                    os.remove(resume.file_path)
                    resume.file_path = None
                    db.commit()
            except OSError:
                pass

            # Stage 4: Send final result
            result = _build_response(
                analysis, entities, all_skills, strong_skills,
                missing_hard, missing_soft, quality,
            )
            # Add pipeline metadata to result
            result["pipeline_version"] = PIPELINE_VERSION
            result["content_hash"] = text_hash
            yield f"event: result\ndata: {json.dumps(result, default=str)}\n\n"

        except Exception as exc:
            logger.error("SSE analysis failed: %s", exc)
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "X-Pipeline-Version": PIPELINE_VERSION,
        },
    )


# Manual skills endpoint removed — CV upload is required for accurate analysis.
