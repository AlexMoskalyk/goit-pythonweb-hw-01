from typing import Optional

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import User
from src.schemas.users import UserCreate
from src.services.auth import get_password_hash
from jose import jwt, JWTError
from src.conf.config import settings


class UserRepository:
    """Repository for user data operations.

    Provides methods for user management, authentication,
    and account operations.
    """

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str):
        """Get a user by email address.

        Args:
            db (AsyncSession): Database session.
            email (str): Email to search for.

        Returns:
            User: Found user or None.
        """
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate):
        """Create a new user.

        Args:
            db (AsyncSession): Database session.
            user_data (UserCreate): User data from schema.

        Returns:
            User: Created user.
        """
        hashed_password = get_password_hash(user_data.password)
        user = User(
            email=user_data.email, hashed_password=hashed_password, role=user_data.role
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def verify_token(db: AsyncSession, token: str):
        """Verify a user's email using a token.

        Args:
            db (AsyncSession): Database session.
            token (str): JWT verification token.

        Returns:
            User: Verified user or None if token invalid.
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            if email is None:
                return None
        except JWTError:
            return None

        user = await UserRepository.get_by_email(db, email)
        if user and not user.is_verified:
            user.is_verified = True
            await db.commit()
            await db.refresh(user)
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str):
        """Authenticate a user with email and password.

        Args:
            db (AsyncSession): Database session.
            email (str): User's email.
            password (str): User's password.

        Returns:
            User: Authenticated user or None if credentials invalid.
        """
        user = await UserRepository.get_by_email(db, email)
        if not user:
            return None

        from src.services.auth import verify_password

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def update_avatar(db: AsyncSession, user: User, avatar_url: str) -> User:
        """Update a user's avatar URL.

        Args:
            db (AsyncSession): Database session.
            user (User): User to update.
            avatar_url (str): New avatar URL.

        Returns:
            User: Updated user.
        """
        user.avatar_url = avatar_url
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def create_password_reset_token(
        db: AsyncSession, email: str
    ) -> Optional[str]:
        """Create a password reset token for a user.

        Args:
            db (AsyncSession): Database session.
            email (str): Email of the user requesting password reset.

        Returns:
            Optional[str]: Reset token or None if user not found.
        """
        user = await UserRepository.get_by_email(db, email)
        if not user:
            return None

        # Create a token with a short expiration (30 minutes)
        from src.services.auth import create_access_token
        from datetime import timedelta

        token_data = {
            "sub": user.email,
            "type": "password_reset",  # Add a type to differentiate from login tokens
        }
        token = create_access_token(token_data, expires_delta=timedelta(minutes=30))
        return token

    @staticmethod
    async def reset_password(
        db: AsyncSession, token: str, new_password: str
    ) -> Optional[User]:
        """Reset a user's password using a valid token.

        Args:
            db (AsyncSession): Database session.
            token (str): Password reset token.
            new_password (str): New password to set.

        Returns:
            Optional[User]: Updated user or None if token invalid.
        """
        try:
            from src.services.auth import SECRET_KEY, ALGORITHM
            from jose import jwt, JWTError

            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            token_type = payload.get("type")

            if email is None or token_type != "password_reset":
                return None
        except JWTError:
            return None

        user = await UserRepository.get_by_email(db, email)
        if user is None:
            return None

        from src.services.auth import get_password_hash
        from src.conf.redis import user_cache

        # Update the password
        user.hashed_password = get_password_hash(new_password)
        db.add(user)
        await db.commit()
        await db.refresh(user)

        # Invalidate cache after password change
        await user_cache.invalidate_user_data(user.email)

        return user
