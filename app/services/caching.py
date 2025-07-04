from redis.asyncio.client import Redis
from app.core.config import settings
from typing import Optional


class CachingService:
    """
    A service for caching data in Redis.
    """

    def __init__(self):
        self.redis = Redis.from_url(settings.redis_url, decode_responses=True)

    async def set(self, key: str, value: str, expiration: Optional[int] = None):
        """
        Sets a key-value pair in the cache.
        """
        if expiration:
            await self.redis.setex(key, expiration, value)
        else:
            await self.redis.set(key, value)

    async def get(self, key: str) -> Optional[str]:
        """
        Gets a value from the cache.
        """
        return await self.redis.get(key)

    async def invalidate(self, key: str):
        """
        Invalidates a key in the cache.
        """
        await self.redis.delete(key)
