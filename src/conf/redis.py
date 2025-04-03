import json
from typing import Optional, Any
import redis.asyncio as redis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from src.conf.config import settings

# Redis connection setup
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    db=0,
    decode_responses=True,
)


# Custom Redis cache manager for user data
class RedisCacheManager:
    def __init__(self, redis_client):
        self.redis_client = redis_client
        self.prefix = "user_cache:"
        self.expiry = 3600  # 1 hour default

    async def set_user_data(self, user_email: str, user_data: dict, expiry: int = None):
        """Store user data in Redis cache"""
        key = f"{self.prefix}{user_email}"
        await self.redis_client.set(
            key, json.dumps(user_data), ex=expiry or self.expiry
        )

    async def get_user_data(self, user_email: str) -> Optional[dict]:
        """Retrieve user data from Redis cache"""
        key = f"{self.prefix}{user_email}"
        data = await self.redis_client.get(key)
        if data:
            return json.loads(data)
        return None

    async def invalidate_user_data(self, user_email: str):
        """Remove user data from cache"""
        key = f"{self.prefix}{user_email}"
        await self.redis_client.delete(key)


# Initialize the cache manager
user_cache = RedisCacheManager(redis_client)


# Setup fastapi-cache
async def setup_redis_cache():
    redis_instance = await redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        password=settings.REDIS_PASSWORD,
        db=0,
        encoding="utf8",
        decode_responses=True,
    )
    FastAPICache.init(RedisBackend(redis_instance), prefix="fastapi-cache:")
