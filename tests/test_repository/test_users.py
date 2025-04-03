import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta

from src.repository.users import UserRepository
from src.schemas.users import UserCreate
from src.entity.models import User


@pytest.mark.asyncio
async def test_get_by_email(override_get_db):
    # Create a user via the repository
    user_data = UserCreate(email="test@example.com", password="password123")

    # Mock password hashing
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    assert created_user.email == "test@example.com"

    # Get the user by email
    user = await UserRepository.get_by_email(override_get_db, "test@example.com")
    assert user is not None
    assert user.email == "test@example.com"

    # Try to get non-existent user
    non_user = await UserRepository.get_by_email(
        override_get_db, "nonexistent@example.com"
    )
    assert non_user is None


@pytest.mark.asyncio
async def test_create_user(override_get_db):
    user_data = UserCreate(email="test@example.com", password="password123")

    # Mock password hashing
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        user = await UserRepository.create(override_get_db, user_data)

    assert user is not None
    assert user.email == "test@example.com"
    assert user.hashed_password == "hashed_password"
    assert not user.is_verified  # By default, users are not verified


@pytest.mark.asyncio
async def test_verify_token(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@example.com", password="password123")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Mock jwt.decode
    with patch("jose.jwt.decode", return_value={"sub": "test@example.com"}):
        user = await UserRepository.verify_token(override_get_db, "test_token")

    assert user is not None
    assert user.email == "test@example.com"
    assert user.is_verified  # User should be verified after token verification

    # Try with invalid token
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        user = await UserRepository.verify_token(override_get_db, "invalid_token")

    assert user is None


@pytest.mark.asyncio
async def test_authenticate_user(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@example.com", password="password123")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Verify the user (needed for authentication)
    with patch("jose.jwt.decode", return_value={"sub": "test@example.com"}):
        await UserRepository.verify_token(override_get_db, "test_token")

    # Mock password verification
    with patch("src.services.auth.verify_password", return_value=True):
        user = await UserRepository.authenticate_user(
            override_get_db, "test@example.com", "password123"
        )

    assert user is not None
    assert user.email == "test@example.com"

    # Try with wrong password
    with patch("src.services.auth.verify_password", return_value=False):
        user = await UserRepository.authenticate_user(
            override_get_db, "test@example.com", "wrong_password"
        )

    assert user is None

    # Try with non-existent user
    user = await UserRepository.authenticate_user(
        override_get_db, "nonexistent@example.com", "password123"
    )
    assert user is None


@pytest.mark.asyncio
async def test_update_avatar(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@example.com", password="password123")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Update avatar
    updated_user = await UserRepository.update_avatar(
        override_get_db, created_user, "https://example.com/avatar.jpg"
    )

    assert updated_user is not None
    assert updated_user.avatar_url == "https://example.com/avatar.jpg"


@pytest.mark.asyncio
async def test_create_password_reset_token(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@example.com", password="password123")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Mock token creation
    with patch("src.services.auth.create_access_token", return_value="reset_token"):
        token = await UserRepository.create_password_reset_token(
            override_get_db, "test@example.com"
        )

    assert token == "reset_token"

    # Try with non-existent user
    token = await UserRepository.create_password_reset_token(
        override_get_db, "nonexistent@example.com"
    )
    assert token is None


@pytest.mark.asyncio
async def test_reset_password(override_get_db):
    # Create a user
    user_data = UserCreate(email="test@example.com", password="password123")
    with patch(
        "src.repository.users.get_password_hash", return_value="hashed_password"
    ):
        created_user = await UserRepository.create(override_get_db, user_data)

    # Mock JWT decoding
    with patch(
        "jose.jwt.decode",
        return_value={"sub": "test@example.com", "type": "password_reset"},
    ):
        # Mock password hashing
        with patch(
            "src.services.auth.get_password_hash", return_value="new_hashed_password"
        ):
            user = await UserRepository.reset_password(
                override_get_db, "reset_token", "new_password"
            )

    assert user is not None
    assert user.hashed_password == "new_hashed_password"

    # Try with invalid token
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        user = await UserRepository.reset_password(
            override_get_db, "invalid_token", "new_password"
        )

    assert user is None

    # Try with wrong token type
    with patch(
        "jose.jwt.decode", return_value={"sub": "test@example.com", "type": "access"}
    ):
        user = await UserRepository.reset_password(
            override_get_db, "wrong_type_token", "new_password"
        )

    assert user is None
