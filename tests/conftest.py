import asyncio
import os
import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.database.db import get_db
from src.entity.models import Base
from src.conf.config import settings
from main import app as app_instance

# Test database URL
TEST_DB_URL = "postgresql+asyncpg://postgres:mypassword@localhost:5432/test_contacts_db"


# Override database dependency
@pytest_asyncio.fixture
async def override_get_db():
    # Create test engine and session
    engine = create_async_engine(TEST_DB_URL, poolclass=NullPool)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    # Create session and return
    async with async_session() as session:
        yield session

    # Clean up
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def app():
    # Override database dependency
    app_instance.dependency_overrides[get_db] = override_get_db

    # Use test Redis (you could mock it instead)
    os.environ["REDIS_HOST"] = "localhost"
    os.environ["REDIS_PORT"] = "6379"
    os.environ["REDIS_PASSWORD"] = ""

    # Mock other external services if needed
    # ...

    yield app_instance

    # Clean up
    app_instance.dependency_overrides.clear()


@pytest_asyncio.fixture
async def async_client(app):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Mock user data fixture
@pytest.fixture
def test_user():
    return {"email": "test@example.com", "password": "password123"}


# Mock contact data fixture
@pytest.fixture
def test_contact():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone_number": "1234567890",
        "birth_date": "2000-01-01T00:00:00Z",
        "additional_info": "Test contact",
    }


# Mock admin user data fixture
@pytest.fixture
def test_admin():
    return {"email": "admin@example.com", "password": "adminpassword", "role": "admin"}


# Mock JWT token for authentication
@pytest.fixture
def mock_jwt(monkeypatch):
    def mock_decode(*args, **kwargs):
        return {"sub": "test@example.com", "type": "access"}

    # Patch jwt.decode
    monkeypatch.setattr("jose.jwt.decode", mock_decode)

    return "test_token"


# Mock Redis fixture
@pytest_asyncio.fixture
async def mock_redis_cache(monkeypatch):
    class MockRedisCache:
        async def get_user_data(self, email):
            if email == "test@example.com":
                return {
                    "id": 1,
                    "email": "test@example.com",
                    "created_at": "2023-01-01T00:00:00",
                    "avatar_url": None,
                    "role": "user",
                }
            return None

        async def set_user_data(self, email, data, expiry=None):
            return True

        async def invalidate_user_data(self, email):
            return True

    # Patch Redis cache
    monkeypatch.setattr("src.conf.redis.user_cache", MockRedisCache())
