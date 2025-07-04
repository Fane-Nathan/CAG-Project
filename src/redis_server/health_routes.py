from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio.client import Redis

from src.redis_server.database import get_redis_cache_client, get_redis_history_client

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Basic server health check.
    """
    return {"status": "ok", "message": "FastAPI Redis server is running."}


@router.get("/health/redis")
async def redis_health_check(
    cache_client: Redis = Depends(get_redis_cache_client),
    history_client: Redis = Depends(get_redis_history_client),
):
    """
    Checks the connection status to the Redis server for both cache and history databases.
    """
    try:
        cache_ping = await cache_client.ping()
        history_ping = await history_client.ping()
        if cache_ping and history_ping:
            return {
                "status": "ok",
                "message": "Redis connection is healthy for both cache and history.",
            }
        else:
            raise HTTPException(status_code=500, detail="Redis connection unhealthy.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis connection failed: {e}")
