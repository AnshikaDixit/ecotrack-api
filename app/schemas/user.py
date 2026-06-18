from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    country: str = "IN"

class UserRead(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    country: str
    region: Optional[str]
    household_size: int
    diet_baseline: str

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    region: Optional[str] = None
    household_size: Optional[int] = None
    diet_baseline: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
