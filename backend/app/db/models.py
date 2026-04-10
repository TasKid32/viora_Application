"""
Database Models — SQLAlchemy ORM definitions.

Uses timezone-aware datetimes throughout.
"""
from sqlalchemy import Column, String, Integer, Boolean, DateTime, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
import uuid

from app.db.database import Base


def generate_uuid() -> str:
    """Generate a new UUID4 string."""
    return str(uuid.uuid4())


def _utc_now() -> datetime:
    """Return current UTC time (timezone-aware)."""
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    avatar_url = Column(Text, nullable=True)
    bio = Column(Text, nullable=True)
    phone_number = Column(String, nullable=True)
    language = Column(String, default="en")
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    # Relationships
    resumes = relationship("Resume", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("SkillAnalysis", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    courses = relationship("Course", back_populates="user", cascade="all, delete-orphan")
    roadmaps = relationship("LearningRoadmap", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    file_path = Column(Text, nullable=True)
    original_filename = Column(String, nullable=True)
    language = Column(String, default="en")
    uploaded_at = Column(DateTime, default=_utc_now)

    # Relationships
    user = relationship("User", back_populates="resumes")
    analysis = relationship("SkillAnalysis", back_populates="resume", uselist=False)

    def __repr__(self) -> str:
        return f"<Resume id={self.id} user_id={self.user_id}>"


class SkillAnalysis(Base):
    __tablename__ = "skill_analyses"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    resume_id = Column(String, ForeignKey("resumes.id"), nullable=True)

    # Analysis results
    predicted_job_title = Column(String, nullable=True)
    experience_level = Column(String, nullable=True)
    strong_skills = Column(JSON, nullable=True)
    missing_skills = Column(JSON, nullable=True)
    extracted_entities = Column(JSON, nullable=True)
    is_archived = Column(Boolean, default=False)

    analyzed_at = Column(DateTime, default=_utc_now)

    # Relationships
    user = relationship("User", back_populates="analyses")
    resume = relationship("Resume", back_populates="analysis")
    roadmap = relationship("LearningRoadmap", back_populates="analysis", uselist=False)

    def __repr__(self) -> str:
        return f"<SkillAnalysis id={self.id} job={self.predicted_job_title}>"


class LearningRoadmap(Base):
    __tablename__ = "learning_roadmaps"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    analysis_id = Column(String, ForeignKey("skill_analyses.id"))
    roadmap_data = Column(JSON, nullable=False)
    is_archived = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utc_now)

    # Relationships
    analysis = relationship("SkillAnalysis", back_populates="roadmap")
    user = relationship("User", back_populates="roadmaps")

    def __repr__(self) -> str:
        return f"<LearningRoadmap id={self.id}>"


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    type = Column(String, nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=_utc_now)

    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification id={self.id} type={self.type}>"


class ChatHistory(Base):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    message = Column(Text, nullable=False)
    reply = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=_utc_now)

    # Relationships
    user = relationship("User", back_populates="chats")

    def __repr__(self) -> str:
        return f"<ChatHistory id={self.id}>"


class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"))
    title = Column(String, nullable=False)
    category = Column(String, nullable=False)
    platform = Column(String, nullable=False)
    completion = Column(Integer, default=0)
    enrolled_date = Column(DateTime, nullable=True)
    completed_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utc_now)
    updated_at = Column(DateTime, default=_utc_now, onupdate=_utc_now)

    # Relationships
    user = relationship("User", back_populates="courses")

    def __repr__(self) -> str:
        return f"<Course id={self.id} title={self.title}>"
