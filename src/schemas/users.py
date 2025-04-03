from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime


class UserRole(str, Enum):
    """User role enumeration.

    Defines the possible roles a user can have in the system.
    """

    USER = "user"  # Regular user with standard permissions
    ADMIN = "admin"  # Administrator with elevated permissions


class UserCreate(BaseModel):
    """Schema for user registration and creation.

    Used to validate data when creating a new user account.

    Attributes:
        email (str): User's email address.
        password (str): User's plaintext password (will be hashed before storage).
        role (UserRole): User's role in the system. Defaults to regular user.
    """

    email: str
    password: str
    role: UserRole = UserRole.USER


class UserResponse(BaseModel):
    """Schema for user data in API responses.

    Represents user data returned to clients, excluding sensitive information.

    Attributes:
        id (int): Unique user identifier.
        email (str): User's email address.
        created_at (datetime): When the user account was created.
        avatar_url (Optional[str]): URL to user's profile image, if any.
        role (UserRole): User's role in the system.
    """

    id: int
    email: str
    created_at: datetime
    avatar_url: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response.

    Used when returning JWT tokens after successful authentication.

    Attributes:
        access_token (str): JWT access token.
        token_type (str): Type of token (usually "bearer").
    """

    access_token: str
    token_type: str


class PasswordResetRequest(BaseModel):
    """Schema for password reset request.

    Used when a user requests a password reset email.

    Attributes:
        email (EmailStr): Email address of the account to reset password for.
    """

    email: EmailStr


class PasswordReset(BaseModel):
    """Schema for password reset confirmation.

    Used when a user submits a new password with their reset token.

    Attributes:
        token (str): Password reset token received via email.
        new_password (str): New password to set for the account.
            Must be at least 8 characters long.
    """

    token: str
    new_password: str = Field(..., min_length=8)
