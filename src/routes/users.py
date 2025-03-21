from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    BackgroundTasks,
    Request,
)
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.entity.models import User
from src.schemas.users import UserCreate, UserResponse, Token
from src.repository.users import UserRepository
from src.services.auth import (
    get_password_hash,
    create_access_token,
    get_current_user,
)
from src.conf.email import send_verification_email

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

    token = create_access_token({"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}
