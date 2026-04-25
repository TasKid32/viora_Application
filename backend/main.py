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

# ─────────────────────────────────────────────
# ⚠️ REMOVE HEAVY PRELOADING (NER + O*NET)
# Render cannot handle 120MB model loading at startup.
# ─────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Viora API starting...")
    yield
    logger.info("Viora API shutting down...")


app = FastAPI(
    title="Viora API",
    description="AI Career Development System - Backend API",
    version=settings.VERSION,
    lifespan=lifespan,
    redirect_slashes=False,
)

# Serve static files
static_dir = "app/static"
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS
ALLOWED_ORIGINS = (
    [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
    if settings.CORS_ORIGINS
    else [
        "http://localhost:8080",
        "http://localhost:3000",
        "http://localhost:5173",
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(resume.router, prefix="/api/resume", tags=["Resume Analysis"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(progress.router, prefix="/api/progress", tags=["Progress"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(roadmap.router, prefix="/api/roadmap", tags=["Learning Roadmap"])
app.include_router(chat.router, prefix="/api/chat", tags=["AI Assistant"])
app.include_router(profile.router, prefix="/api/profile", tags=["Profile"])
app.include_router(courses.router, prefix="/api/courses", tags=["Courses"])

# Uploads
upload_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=upload_dir), name="uploads")


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


# ─────────────────────────────────────────────
# ⭐ REQUIRED FOR RENDER — dynamic port binding
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
