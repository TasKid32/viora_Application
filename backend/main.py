"""
Viora Backend API - Main Application.

Uses structured logging instead of print().
"""
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.api.v1 import auth, resume, dashboard, progress, notifications, chat, profile, roadmap, courses
from app.core.config import settings
from app.core.logging import get_logger
from app.db.database import engine
from app.db import models

logger = get_logger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup — preload heavy models to avoid cold start latency
    logger.info("Viora API v%s starting...", settings.VERSION)

# Initialize event-driven architecture
    from app.core.events import event_dispatcher
    from app.listeners.notification_listener import setup_notification_listeners
    setup_notification_listeners(event_dispatcher)
    logger.info("Event-driven architecture initialized")

    # Preload Viora NER model (~3s on first load, ~120MB)
    try:
        from app.services.viora_ner_service import get_ner_service
        ner = get_ner_service()
        ner.warmup()  # ← Actually trigger model loading!
        if ner.is_available:
            logger.info("Viora NER model preloaded successfully")
        else:
            logger.warning("Viora NER model not available — will skip NER in analysis")
    except Exception as e:
        logger.warning("Could not preload NER model: %s", e)

    # Preload O*NET taxonomy data (~0.5s, ~1016 occupations)
    try:
        from app.services.onet_service import get_onet_service
        onet = get_onet_service()
        onet._ensure_initialized()  # ← Actually trigger data loading!
        logger.info("O*NET taxonomy preloaded: %d occupations", len(onet._occupations))
    except Exception as e:
        logger.warning("Could not preload O*NET data: %s", e)

    yield
    # Shutdown
    logger.info("Viora API shutting down...")


app = FastAPI(
    title="Viora API",
    description="AI Career Development System - Backend API",
    version=settings.VERSION,
    lifespan=lifespan,
)
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# CORS middleware — configurable from .env (B4 Fix)
ALLOWED_ORIGINS = (
    [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    if settings.CORS_ORIGINS
    else [
        "http://localhost:8080",   # Flutter web dev
        "http://localhost:3000",   # General dev
        "http://localhost:5173",   # Vite dev
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume Analysis"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["Learning Roadmap"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Assistant"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])

# Serve uploaded files (avatars, etc.) — creates dir if needed
import os as _os
_uploads_dir = _os.path.abspath(settings.UPLOAD_DIR)
_os.makedirs(_uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=_uploads_dir), name="uploads")


@app.get("/")
async def root():
    return {
        "message": f"Viora API v{settings.VERSION}",
        "status": "running",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
