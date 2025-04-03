from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
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


class Token(BaseModel):
    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)
