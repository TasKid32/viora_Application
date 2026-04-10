"""Chat schemas — Chat message and response models."""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ChatMessage(BaseModel):
    message: str
    context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    suggestions: List[str]
    timestamp: datetime
