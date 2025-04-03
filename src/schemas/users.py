from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


# Schema for user registration
class UserCreate(BaseModel):
    email: str
    password: str
    role: UserRole = UserRole.USER


# Schema for user response (without password)
class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime
    avatar_url: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True


# ✅ Schema for JWT Token Response
class Token(BaseModel):
    access_token: str
    token_type: str
