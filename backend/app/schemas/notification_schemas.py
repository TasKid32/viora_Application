"""Notification schemas — Notification response model."""
from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    id: str
    type: str
    title: str
    message: str
    timestamp: str
    is_read: bool
    icon: str

    model_config = ConfigDict(from_attributes=True)
