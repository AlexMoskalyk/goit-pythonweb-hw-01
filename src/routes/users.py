from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import (
    UserCreate,
    UserResponse,
    Token,
    UserRole,
    PasswordResetRequest,
    PasswordReset,
)
from src.repository.users import UserRepository
from src.services.auth import (
    get_password_hash,
    create_access_token,
    get_current_user,
    admin_only,
)
from src.conf.email import send_verification_email, send_password_reset_email

from slowapi import Limiter
from slowapi.util import get_remote_address

from fastapi import UploadFile, File
import cloudinary.uploader


router = APIRouter(prefix="/users", tags=["Users"])

# Configure rate limiter
limiter = Limiter(key_func=get_remote_address)


@router.post("/avatar", response_model=UserResponse)
async def upload_avatar(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if user is an admin or has a default avatar
    if current_user.role != UserRole.ADMIN and current_user.avatar_url is not None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can change their avatar after setting one",
        )

    result = cloudinary.uploader.upload(
        file.file, public_id=f"user_{current_user.id}_avatar", overwrite=True
    )
    url = result.get("secure_url")
    updated_user = await UserRepository.update_avatar(db, current_user, url)
    return updated_user


@router.get("/me")
@limiter.limit("5/minute")
async def get_me(
    request: Request,
    current_user: UserResponse = Depends(get_current_user),
):
    return current_user


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    existing_user = await UserRepository.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=409, detail="User already exists")

    new_user = await UserRepository.create(db, user_data)
    token = create_access_token({"sub": new_user.email})
    background_tasks.add_task(send_verification_email, new_user.email, token)

    return new_user


@router.get("/verify")
async def verify_email(token: str, db: AsyncSession = Depends(get_db)):
    user = await UserRepository.verify_token(db, token)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    return {"message": "Email verified successfully!"}


@router.post("/login", response_model=Token)
async def login(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    user = await UserRepository.authenticate_user(
        db, user_data.email, user_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )

    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Email is not verified"
        )

    token = create_access_token({"sub": user.email, "type": "access"})
    return {"access_token": token, "token_type": "bearer"}


@router.post("/promote-to-admin/{user_id}", response_model=UserResponse)
async def promote_to_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(admin_only),
):
    # Find the user to promote
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update role to admin
    user.role = UserRole.ADMIN
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/password-reset-request")
@limiter.limit("3/hour")  # Limit requests to prevent abuse
async def request_password_reset(
    request_data: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Request a password reset email."""
    # Generate a token
    token = await UserRepository.create_password_reset_token(db, request_data.email)

    # If the user exists, send an email
    if token:
        background_tasks.add_task(send_password_reset_email, request_data.email, token)

    # Always return success to prevent email enumeration attacks
    return {
        "message": "If your email exists in our system, you will receive a password reset link"
    }


@router.post("/reset-password")
async def reset_password(
    reset_data: PasswordReset,
    db: AsyncSession = Depends(get_db),
):
    """Reset a user's password with a valid token."""
    user = await UserRepository.reset_password(
        db, reset_data.token, reset_data.new_password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token",
        )

    return {"message": "Password has been reset successfully"}
