from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class Goal(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    title: str
    target_reduction_percent: float
    baseline_co2e_kg: float
    period_start: datetime
    period_end: datetime
    status: str = Field(default="active") # active/completed/failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
