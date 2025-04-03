import pytest
from unittest.mock import AsyncMock, patch
from jose import jwt
from datetime import datetime


@pytest.mark.asyncio
async def test_register_user(async_client, test_user):
    # Mock email sending to avoid actual email dispatch
    with patch(
        "src.conf.email.send_verification_email", new_callable=AsyncMock
    ) as mock_send_email:
        response = await async_client.post("/users/register", json=test_user)

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "password" not in data
    mock_send_email.assert_called_once()


@pytest.mark.asyncio
async def test_register_existing_user(async_client, test_user):
    # Register a user
    await async_client.post("/users/register", json=test_user)

    # Try to register the same user again
    response = await async_client.post("/users/register", json=test_user)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_user(async_client, test_user):
    # Register and verify a user
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Mock verify_token to return a verified user
    with patch(
        "src.repository.users.UserRepository.verify_token", new_callable=AsyncMock
    ) as mock_verify:
        # Create a verified user mock
        from src.entity.models import User

        user_mock = User(
            id=1,
            email=test_user["email"],
            hashed_password="hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )
        mock_verify.return_value = user_mock

        # Verify the user
        await async_client.get("/users/verify?token=test_token")

    # Login
    response = await async_client.post("/users/login", json=test_user)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_unverified_user(async_client, test_user):
    # Register a user but don't verify
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Try to login without verification
    response = await async_client.post("/users/login", json=test_user)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_current_user(async_client, mock_jwt, mock_redis_cache):
    # Set auth header with mock token
    headers = {"Authorization": f"Bearer {mock_jwt}"}

    response = await async_client.get("/users/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_password_reset_request(async_client, test_user):
    # Register a user
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Mock email sending
    with patch(
        "src.conf.email.send_password_reset_email", new_callable=AsyncMock
    ) as mock_send:
        response = await async_client.post(
            "/users/password-reset-request", json={"email": test_user["email"]}
        )

    assert response.status_code == 200
    assert "message" in response.json()
    mock_send.assert_called_once()


@pytest.mark.asyncio
async def test_reset_password(async_client, test_user):
    # Register a user
    with patch("src.conf.email.send_verification_email", new_callable=AsyncMock):
        await async_client.post("/users/register", json=test_user)

    # Mock reset_password to return a user
    with patch(
        "src.repository.users.UserRepository.reset_password", new_callable=AsyncMock
    ) as mock_reset:
        from src.entity.models import User

        mock_reset.return_value = User(
            id=1,
            email=test_user["email"],
            hashed_password="new_hashed_password",
            created_at=datetime.utcnow(),
            is_verified=True,
        )

        response = await async_client.post(
            "/users/reset-password",
            json={"token": "test_token", "new_password": "new_password123"},
        )

    assert response.status_code == 200
    assert "message" in response.json()
