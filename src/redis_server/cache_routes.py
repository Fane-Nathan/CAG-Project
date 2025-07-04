from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio.client import Redis
from typing import Optional

from src.redis_server.database import get_redis_cache_client

router = APIRouter()


@router.post("/set")
async def set_cache_entry(
    key: str,
    value: str,
    expiration: Optional[int] = None,
    cache_client: Redis = Depends(get_redis_cache_client),
):
    """
    Stores a key-value pair in the cache with an optional expiration time.
    """
    try:
        if expiration:
            await cache_client.setex(key, expiration, value)
        else:
            await cache_client.set(key, value)
        return {"message": f"Cache entry for key '{key}' set successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set cache entry: {e}")


@router.get("/get/{key}")
async def get_cache_entry(
    key: str, cache_client: Redis = Depends(get_redis_cache_client)
):
    """
    Retrieves the value associated with a given key from the cache.
    """
    try:
        value = await cache_client.get(key)
        if value is None:
            raise HTTPException(
                status_code=404, detail=f"Cache entry for key '{key}' not found."
            )
        return {"key": key, "value": value}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get cache entry: {e}")


@router.delete("/invalidate/{key}")
async def invalidate_cache_entry(
    key: str, cache_client: Redis = Depends(get_redis_cache_client)
):
    """
    Invalidates (deletes) a cache entry by its key.
    """
    try:
        deleted_count = await cache_client.delete(key)
        if deleted_count == 0:
            raise HTTPException(
                status_code=404, detail=f"Cache entry for key '{key}' not found."
            )
        return {"message": f"Cache entry for key '{key}' invalidated successfully."}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to invalidate cache entry: {e}"
        )


# TODO: Integrate GPTCache for LLM response caching
# This will likely involve a separate module that uses GPTCache and then exposes
# its own set of endpoints or integrates directly with the existing ones.
# For now, basic Redis caching is implemented.
