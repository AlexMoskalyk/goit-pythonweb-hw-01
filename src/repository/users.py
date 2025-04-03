from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.entity.models import User
from src.schemas.users import UserCreate
from src.services.auth import get_password_hash
from jose import jwt, JWTError
from src.conf.config import settings


class UserRepository:
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(db: AsyncSession, user_data: UserCreate):
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
        user = await UserRepository.get_by_email(db, email)
        if not user:
            return None

        from src.services.auth import verify_password

        if not verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def update_avatar(db: AsyncSession, user: User, avatar_url: str) -> User:
        user.avatar_url = avatar_url
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
