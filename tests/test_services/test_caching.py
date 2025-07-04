import pytest
from unittest.mock import AsyncMock, patch
from app.services.caching import CachingService


@pytest.mark.asyncio
@patch("redis.asyncio.client.Redis.from_url")
async def test_caching_service(mock_from_url):
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis
    caching_service = CachingService()

    await caching_service.set("test_key", "test_value")
    mock_redis.set.assert_called_once_with("test_key", "test_value")

    await caching_service.set("test_key_exp", "test_value_exp", 3600)
    mock_redis.setex.assert_called_once_with("test_key_exp", 3600, "test_value_exp")

    await caching_service.get("test_key")
    mock_redis.get.assert_called_once_with("test_key")

    await caching_service.invalidate("test_key")
    mock_redis.delete.assert_called_once_with("test_key")
