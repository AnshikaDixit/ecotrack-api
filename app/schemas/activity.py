from datetime import datetime
from pydantic import BaseModel
from typing import Optional

class ActivityCreate(BaseModel):
    category: str
    subtype: str
    quantity: float
    unit: str
    activity_date: datetime
    notes: Optional[str] = None

class ActivityRead(BaseModel):
    id: int
    user_id: int
    category: str
    subtype: str
    quantity: float
    unit: str
    activity_date: datetime
    co2e_kg: float
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
