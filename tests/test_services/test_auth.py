import pytest
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException

from src.services.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)


def test_get_password_hash():
    # Test that password hashing works
    hashed = get_password_hash("password123")
    assert hashed != "password123"
    assert isinstance(hashed, str)
    assert len(hashed) > 20  # bcrypt hashes are typically longer


def test_verify_password():
    # Test password verification
    hashed = get_password_hash("password123")
    assert verify_password("password123", hashed)
    assert not verify_password("wrong_password", hashed)


def test_create_access_token():
    # Test token creation
    token = create_access_token({"sub": "test@example.com"})
    assert isinstance(token, str)

    # Test with expiry
    token = create_access_token({"sub": "test@example.com"}, timedelta(minutes=30))
    assert isinstance(token, str)


@pytest.mark.asyncio
async def test_get_current_user(override_get_db, mock_jwt, mock_redis_cache):
    # Mock jwt.decode to return a valid payload
    with patch(
        "jose.jwt.decode", return_value={"sub": "test@example.com", "type": "access"}
    ):
        # Create user to return
        from src.entity.models import User

        user = User(
            id=1,
            email="test@example.com",
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        # Mock get_by_email
        with patch(
            "src.repository.users.UserRepository.get_by_email", return_value=user
        ):
            current_user = await get_current_user(mock_jwt, override_get_db)

    assert current_user is not None
    assert current_user.email == "test@example.com"

    # Test with invalid token
    with patch("jose.jwt.decode", side_effect=Exception("Invalid token")):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user("invalid_token", override_get_db)

    assert exc_info.value.status_code == 401

    # Test with missing subject
    with patch("jose.jwt.decode", return_value={"type": "access"}):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_jwt, override_get_db)

    assert exc_info.value.status_code == 401

    # Test with wrong token type
    with patch(
        "jose.jwt.decode",
        return_value={"sub": "test@example.com", "type": "password_reset"},
    ):
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(mock_jwt, override_get_db)

    assert exc_info.value.status_code == 401

    # Test with non-existent user
    with patch(
        "jose.jwt.decode", return_value={"sub": "test@example.com", "type": "access"}
    ):
        with patch(
            "src.repository.users.UserRepository.get_by_email", return_value=None
        ):
            with pytest.raises(HTTPException) as exc_info:
                await get_current_user(mock_jwt, override_get_db)

    assert exc_info.value.status_code == 401
