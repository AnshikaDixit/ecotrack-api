from pydantic import BaseModel
from typing import Dict, List, Optional

class FootprintSummary(BaseModel):
    total_co2e_kg: float
    category_breakdown: Dict[str, float]
    eco_points: int = 0
    # We could add trends here too, but MVP keeps it simple
    
class Insight(BaseModel):
    category: str
    trigger: str
    recommendation: str
    estimated_savings_kg: Optional[float] = None
    insight_key: str
