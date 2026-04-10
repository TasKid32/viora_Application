"""Resume schemas — Upload, analysis request/response models."""
from pydantic import BaseModel
from typing import Any, Optional, List
from datetime import datetime


class ResumeUploadResponse(BaseModel):
    file_id: str
    filename: str
    size: int
    uploaded_at: datetime


class SkillsInput(BaseModel):
    skills: List[str]


class AnalysisRequest(BaseModel):
    file_id: str
    additional_skills: Optional[List[str]] = None


class SkillProficiency(BaseModel):
    name: str
    proficiency: int


class AnalysisResponse(BaseModel):
    analysis_id: str
    user_profile: dict
    gap_analysis: dict
    job_opportunities: Optional[List[str]] = None
    recommendations: Optional[List[Any]] = None
    cv_quality: Optional[dict] = None
    processed_at: datetime
