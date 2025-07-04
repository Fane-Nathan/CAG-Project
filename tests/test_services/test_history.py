import pytest
from unittest.mock import AsyncMock, patch
from app.services.history import HistoryService
import json


@pytest.mark.asyncio
@patch("redis.asyncio.client.Redis.from_url")
async def test_history_service(mock_from_url):
    mock_redis = AsyncMock()
    mock_from_url.return_value = mock_redis
    history_service = HistoryService()

    await history_service.add_turn("test_user", "test_message", "user")
    mock_redis.rpush.assert_called_once_with(
        "history:test_user", json.dumps({"message": "test_message", "role": "user"})
    )

    await history_service.get_history("test_user")
    mock_redis.lrange.assert_called_once_with("history:test_user", 0, -1)

    await history_service.clear_history("test_user")
    mock_redis.delete.assert_called_once_with("history:test_user")
