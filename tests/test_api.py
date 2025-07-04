import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
@patch("app.services.crawler.CrawlerService.crawl")
async def test_crawl_endpoint(mock_crawl):
    mock_crawl.return_value = "test markdown"
    response = client.post("/crawl", json={"url": "https://example.com"})
    assert response.status_code == 200
    assert response.json() == {"markdown": "test markdown"}
    mock_crawl.assert_called_once_with("https://example.com")


@pytest.mark.asyncio
@patch("app.services.llm_provider.LLMProvider.generate_content")
async def test_generate_endpoint(mock_generate):
    mock_generate.return_value = "test content"
    response = client.post("/generate", json={"prompt": "test prompt"})
    assert response.status_code == 200
    assert response.json() == {"text": "test content"}
    mock_generate.assert_called_once_with("test prompt")


@pytest.mark.asyncio
@patch("app.services.history.HistoryService.add_turn")
async def test_add_chat_turn_endpoint(mock_add_turn):
    response = client.post(
        "/history/add",
        json={"user_id": "test_user", "message": "test message", "role": "user"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Chat turn added successfully."}
    mock_add_turn.assert_called_once_with("test_user", "test message", "user")


@pytest.mark.asyncio
@patch("app.services.history.HistoryService.get_history")
async def test_get_chat_history_endpoint(mock_get_history):
    mock_get_history.return_value = [{"message": "test message", "role": "user"}]
    response = client.get("/history/get/test_user")
    assert response.status_code == 200
    assert response.json() == {
        "history": [{"message": "test message", "role": "user"}]
    }
    mock_get_history.assert_called_once_with("test_user")
