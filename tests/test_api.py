import pytest
from unittest.mock import patch, AsyncMock

# client = TestClient(app) # Removed global client


@pytest.mark.asyncio
async def test_crawl_endpoint(test_client):
    # Mock the crawl method of CrawlerService
    with patch("app.services.crawler.CrawlerService.crawl", new_callable=AsyncMock) as mock_crawl:
        mock_crawl.return_value = "test markdown"
        response = test_client.post("/crawl", json={"url": "https://example.com"})
        assert response.status_code == 200
        assert response.json() == {"markdown": "test markdown"}
        mock_crawl.assert_called_once_with("https://example.com")


@pytest.mark.asyncio
async def test_generate_endpoint_no_cache(test_client, override_dependencies):
    mock_llm_provider_instance, mock_gptcache_service_instance, _ = override_dependencies

    # Setup the mock service
    mock_gptcache_service_instance.get.return_value = None
    
    # You also need to mock the llm provider in this fixture
    mock_llm_provider_instance.generate_content.return_value = "test content"

    response = test_client.post("/generate", json={"prompt": "test prompt"})
    
    assert response.status_code == 200
    assert response.json() == {"text": "test content"}
    mock_gptcache_service_instance.get.assert_called_once_with("test prompt")
    mock_gptcache_service_instance.set.assert_called_once_with("test prompt", "test content")


@pytest.mark.asyncio
async def test_add_chat_turn_endpoint(test_client, override_dependencies):
    _, _, mock_history_service_instance = override_dependencies
    mock_history_service_instance.add_turn.return_value = None # add_turn is async

    response = test_client.post(
        "/history/add",
        json={"user_id": "test_user", "message": "test message", "role": "user"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Chat turn added successfully."}
    mock_history_service_instance.add_turn.assert_called_once_with("test_user", "test message", "user")


@pytest.mark.asyncio
async def test_get_chat_history_endpoint(test_client, override_dependencies):
    _, _, mock_history_service_instance = override_dependencies
    mock_history_service_instance.get_history.return_value = [{"message": "test message", "role": "user"}]

    response = test_client.get("/history/get/test_user")
    assert response.status_code == 200
    assert response.json() == {
        "history": [{"message": "test message", "role": "user"}]
    }
    mock_history_service_instance.get_history.assert_called_once_with("test_user")
