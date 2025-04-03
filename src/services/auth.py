from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.redis import user_cache
from src.database.db import get_db
from src.schemas.users import UserResponse, UserRole
from src.repository.users import UserRepository
from src.conf.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

# JWT Config
SECRET_KEY = settings.SECRET_KEY  # Load from .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Hash a password
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


# Verify a password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# Create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# Get current user from JWT token
async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        token_type: str = payload.get(
            "type", "access"
        )  # Default to "access" for backwards compatibility

        if email is None:
            raise credentials_exception

        # Ensure we're not using a password reset token for authentication
        if token_type == "password_reset":
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Try to get user from Redis cache first
    cached_user = await user_cache.get_user_data(email)

    if cached_user:
        # Convert cached data to UserResponse model
        from src.schemas.users import UserResponse

        return UserResponse(**cached_user)

    # If not in cache, get from database
    user = await UserRepository.get_by_email(db, email)
    if user is None:
        raise credentials_exception

    # Convert to dict and cache for future requests
    user_data = {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "avatar_url": user.avatar_url,
        "role": user.role,
    }
    await user_cache.set_user_data(email, user_data)

    return user


# Add this function
def RoleChecker(allowed_roles: list[UserRole]):
    async def check_role(
        current_user: UserResponse = Depends(get_current_user),
    ) -> UserResponse:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user

    return check_role


# Admin-only check
admin_only = RoleChecker([UserRole.ADMIN])
