"""Progress schemas — Weekly activity and completed course models."""
from pydantic import BaseModel


class WeeklyActivity(BaseModel):
    Mon: int
    Tue: int
    Wed: int
    Thu: int
    Fri: int
    Sat: int
    Sun: int


class CompletedCourse(BaseModel):
    title: str
    category: str
    completion: int
