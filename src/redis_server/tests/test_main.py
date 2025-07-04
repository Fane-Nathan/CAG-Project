import pytest
from fastapi.testclient import TestClient
from src.redis_server.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_health_check():
    response = client.get("/health/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "FastAPI Redis server is running.",
    }


@pytest.mark.asyncio
async def test_redis_health_check(override_redis_clients):
    mock_cache_client, mock_history_client = override_redis_clients
    response = client.get("/health/health/redis")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "message": "Redis connection is healthy for both cache and history.",
    }
    mock_cache_client.ping.assert_called_once()
    mock_history_client.ping.assert_called_once()


@pytest.mark.asyncio
async def test_redis_health_check_failure(override_redis_clients):
    mock_cache_client, mock_history_client = override_redis_clients
    mock_cache_client.ping.return_value = False
    response = client.get("/health/health/redis")
    assert response.status_code == 500
    assert "Redis connection unhealthy." in response.json()["detail"]
