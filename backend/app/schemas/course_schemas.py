"""Course schemas — Course CRUD models."""
from pydantic import BaseModel, ConfigDict
from typing import Optional


class CourseResponse(BaseModel):
    id: str
    title: str
    category: str
    platform: str
    completion: int
    enrolled_date: Optional[str] = None
    completed_date: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CourseCreate(BaseModel):
    title: str
    category: str
    platform: str
    completion: int = 0


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[str] = None
    platform: Optional[str] = None
    completion: Optional[int] = None
    completed_date: Optional[str] = None
