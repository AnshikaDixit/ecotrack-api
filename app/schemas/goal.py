from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class GoalCreate(BaseModel):
    title: str
    target_reduction_percent: float
    baseline_co2e_kg: float
    period_start: datetime
    period_end: datetime

class GoalRead(BaseModel):
    id: int
    user_id: int
    title: str
    target_reduction_percent: float
    baseline_co2e_kg: float
    current_co2e_kg: float = 0.0
    period_start: datetime
    period_end: datetime
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class GoalUpdate(BaseModel):
    status: Optional[str] = None
    title: Optional[str] = None
