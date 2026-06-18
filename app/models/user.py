from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    full_name: Optional[str] = None
    country: str = Field(default="IN")
    region: Optional[str] = None
    household_size: int = Field(default=1)
    diet_baseline: str = Field(default="omnivore") # vegan/vegetarian/omnivore/high_meat

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
