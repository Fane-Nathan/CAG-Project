import sys
import os
import pytest
from unittest.mock import AsyncMock

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.redis_server.main import app
from src.redis_server.database import get_redis_cache_client, get_redis_history_client


@pytest.fixture(autouse=True)
def override_redis_clients():
    mock_cache_client = AsyncMock()
    mock_cache_client.set.return_value = True
    mock_cache_client.setex.return_value = True
    mock_cache_client.get.return_value = None
    mock_cache_client.delete.return_value = 0
    mock_cache_client.ping.return_value = True

    mock_history_client = AsyncMock()
    mock_history_client.rpush.return_value = 1
    mock_history_client.lrange.return_value = []
    mock_history_client.delete.return_value = 0
    mock_history_client.ping.return_value = True

    app.dependency_overrides[get_redis_cache_client] = lambda: mock_cache_client
    app.dependency_overrides[get_redis_history_client] = lambda: mock_history_client

    yield mock_cache_client, mock_history_client

    app.dependency_overrides = {}