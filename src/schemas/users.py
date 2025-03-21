from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime


# Schema for user registration
class UserCreate(BaseModel):
    email: str
    password: str


# Schema for user response (without password)
class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


# ✅ Schema for JWT Token Response
class Token(BaseModel):
    access_token: str
    token_type: str
