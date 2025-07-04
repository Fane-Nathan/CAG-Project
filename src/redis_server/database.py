import redis.asyncio as redis
from redis.asyncio.client import Redis
from src.redis_server.settings import settings


class RedisClient:
    """
    Manages asynchronous Redis connections for caching and chat history.
    """

    _cache_client: Redis | None = None
    _history_client: Redis | None = None

    @classmethod
    async def get_cache_client(cls) -> Redis:
        """
        Returns an asynchronous Redis client for caching.
        Initializes the client if it doesn't exist.
        """
        if cls._cache_client is None:
            cls._cache_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_cache_db,
                decode_responses=True,  # Decode responses to Python strings
            )
        return cls._cache_client

    @classmethod
    async def get_history_client(cls) -> Redis:
        """
        Returns an asynchronous Redis client for chat history.
        Initializes the client if it doesn't exist.
        """
        if cls._history_client is None:
            cls._history_client = redis.Redis(
                host=settings.redis_host,
                port=settings.redis_port,
                password=settings.redis_password,
                db=settings.redis_history_db,
                decode_responses=True,  # Decode responses to Python strings
            )
        return cls._history_client

    @classmethod
    async def close_connections(cls):
        """
        Closes all active Redis client connections.
        """
        if cls._cache_client:
            await cls._cache_client.close()
            cls._cache_client = None
        if cls._history_client:
            await cls._history_client.close()
            cls._history_client = None


async def get_redis_cache_client() -> Redis:
    """
    Dependency for FastAPI to get the cache Redis client.
    """
    return await RedisClient.get_cache_client()


async def get_redis_history_client() -> Redis:
    """
    Dependency for FastAPI to get the history Redis client.
    """
    return await RedisClient.get_history_client()
