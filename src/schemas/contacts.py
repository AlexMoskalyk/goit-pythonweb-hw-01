from datetime import datetime
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class ContactCreate(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone_number: str = Field(..., min_length=5, max_length=20)
    birth_date: datetime
    additional_info: Optional[str] = None


class ContactResponse(ContactCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
