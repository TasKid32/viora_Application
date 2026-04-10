"""Dashboard schemas — Dashboard response model."""
from pydantic import BaseModel
from typing import List


class DashboardResponse(BaseModel):
    user: dict
    progress: dict
    quick_actions: List[dict]
