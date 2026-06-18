from typing import Optional
from sqlmodel import SQLModel, Field

class EmissionFactor(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    category: str
    subtype: str
    region: Optional[str] = Field(default=None) # null = global default
    factor_value: float
    unit: str
    source_note: Optional[str] = None
