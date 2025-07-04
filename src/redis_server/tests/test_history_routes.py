import pytest
from fastapi.testclient import TestClient
import json
from src.redis_server.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_add_chat_turn(override_redis_clients):
    _, mock_history_client = override_redis_clients
    response = client.post(
        "/history/add?user_id=test_user_1&message=Hello&role=user",
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Chat turn added for user 'test_user_1'."}
    mock_history_client.rpush.assert_called_once_with(
        "history:test_user_1", json.dumps({"message": "Hello", "role": "user"})
    )


@pytest.mark.asyncio
async def test_get_chat_history(override_redis_clients):
    _, mock_history_client = override_redis_clients
    mock_history_client.lrange.return_value = [
        json.dumps({"message": "Hello", "role": "user"}).encode("utf-8"),
        json.dumps({"message": "Hi there!", "role": "model"}).encode("utf-8"),
    ]
    response = client.get("/history/get/test_user_2")
    assert response.status_code == 200
    assert response.json() == [
        {"message": "Hello", "role": "user"},
        {"message": "Hi there!", "role": "model"},
    ]
    mock_history_client.lrange.assert_called_once_with(
        "history:test_user_2", 0, -1
    )


@pytest.mark.asyncio
async def test_clear_chat_history(override_redis_clients):
    _, mock_history_client = override_redis_clients
    mock_history_client.delete.return_value = 1
    response = client.delete("/history/clear/test_user_3")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Chat history cleared for user 'test_user_3'."
    }
    mock_history_client.delete.assert_called_once_with("history:test_user_3")


@pytest.mark.asyncio
async def test_clear_chat_history_not_found(override_redis_clients):
    _, mock_history_client = override_redis_clients
    mock_history_client.delete.return_value = 0
    response = client.delete("/history/clear/non_existing_user")
    assert response.status_code == 404
    assert response.json() == {
        "detail": "Chat history for user 'non_existing_user' not found."
    }