import pytest
from fastapi.testclient import TestClient
from src.redis_server.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_set_cache_entry(override_redis_clients):
    mock_cache_client, _ = override_redis_clients
    response = client.post("/cache/set?key=test_key&value=test_value")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Cache entry for key 'test_key' set successfully."
    }
    mock_cache_client.set.assert_called_once_with("test_key", "test_value")


@pytest.mark.asyncio
async def test_set_cache_entry_with_expiration(override_redis_clients):
    mock_cache_client, _ = override_redis_clients
    response = client.post(
        "/cache/set?key=test_key_exp&value=test_value_exp&expiration=3600"
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "Cache entry for key 'test_key_exp' set successfully."
    }
    mock_cache_client.setex.assert_called_once_with(
        "test_key_exp", 3600, "test_value_exp"
    )


@pytest.mark.asyncio
async def test_get_cache_entry(override_redis_clients):
    mock_cache_client, _ = override_redis_clients
    mock_cache_client.get.return_value = "cached_value"
    response = client.get("/cache/get/existing_key")
    assert response.status_code == 200
    assert response.json() == {"key": "existing_key", "value": "cached_value"}
    mock_cache_client.get.assert_called_once_with("existing_key")


@pytest.mark.asyncio
async def test_get_cache_entry_not_found(override_redis_clients):
    mock_cache_client, _ = override_redis_clients
    mock_cache_client.get.return_value = None
    response = client.get("/cache/get/non_existing_key")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cache entry for key 'non_existing_key' not found."
    }


@pytest.mark.asyncio
async def test_invalidate_cache_entry(override_redis_clients):
    mock_cache_client, _ = override_redis_clients
    mock_cache_client.delete.return_value = 1
    response = client.delete("/cache/invalidate/key_to_invalidate")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Cache entry for key 'key_to_invalidate' invalidated successfully."
    }
    mock_cache_client.delete.assert_called_once_with("key_to_invalidate")


@pytest.mark.asyncio
async def test_invalidate_cache_entry_not_found(override_redis_clients):
    mock_cache_client, _ = override_redis_clients
    mock_cache_client.delete.return_value = 0
    response = client.delete("/cache/invalidate/non_existing_key")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Cache entry for key 'non_existing_key' not found."
    }