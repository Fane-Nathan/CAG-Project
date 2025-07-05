import pytest
from unittest.mock import patch, AsyncMock

# client = TestClient(app) # Removed global client


@pytest.mark.asyncio
async def test_crawl_endpoint(test_client, override_dependencies):
    # Mock the crawl_with_metadata method of CrawlerService
    with patch("app.services.crawler.CrawlerService.crawl_with_metadata", new_callable=AsyncMock) as mock_crawl:
        mock_crawl.return_value = {
            "markdown": "test markdown",
            "timestamp": 1234567890,
            "cached_at": None
        }
        response = test_client.post("/crawl", json={"url": "https://example.com", "use_cache": True})
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["markdown"] == "test markdown"
        assert response_data["cached"] == False
        assert response_data["timestamp"] == 1234567890
        mock_crawl.assert_called_once_with("https://example.com", use_cache=True)


@pytest.mark.asyncio
async def test_generate_endpoint_no_cache(test_client, override_dependencies):
    mock_llm_provider_instance, mock_gptcache_service_instance, _ = override_dependencies

    # Setup the mock service for new GPTCache methods
    mock_gptcache_service_instance.get_llm_response = AsyncMock(return_value=None)  # Simulate no cache hit
    mock_gptcache_service_instance.set_llm_response = AsyncMock()  # Mock the async set method
    
    # You also need to mock the llm provider in this fixture
    mock_llm_provider_instance.generate_content.return_value = "test content"

    response = test_client.post("/generate", json={"prompt": "This is a valid test prompt for testing", "use_cache": True})
    
    assert response.status_code == 200
    response_data = response.json()
    assert response_data["text"] == "test content"
    assert response_data["cached"] == False
    mock_gptcache_service_instance.get_llm_response.assert_called_once_with("This is a valid test prompt for testing")
    mock_gptcache_service_instance.set_llm_response.assert_awaited_once_with("This is a valid test prompt for testing", "test content")


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


@pytest.mark.asyncio
async def test_cag_endpoint(test_client, override_dependencies):
    """Test the unified Cache-Augmented Generation endpoint"""
    mock_llm_provider_instance, mock_gptcache_service_instance, mock_history_service_instance = override_dependencies
    
    # Mock crawler service at the class level
    with patch("app.services.crawler.CrawlerService.crawl_with_metadata", new_callable=AsyncMock) as mock_crawl:
        # Mock crawl response
        mock_crawl.return_value = {
            "markdown": "# Test Content\nThis is test content from the website.",
            "title": "Test Page",
            "timestamp": 1234567890,
            "success": True,
            "status_code": 200
        }
        
        # Mock LLM response
        mock_llm_provider_instance.generate_content.return_value = "Based on the content, here is the answer to your query."
        
        # Test CAG request
        response = test_client.post("/cag", json={
            "url": "https://example.com",
            "query": "What is this page about and what does it contain?",
            "user_id": "test_user",
            "use_cache": True,
            "include_history": False
        })
        
        assert response.status_code == 200
        response_data = response.json()
        
        # Verify response structure
        assert "response" in response_data
        assert "url" in response_data
        assert "query" in response_data
        assert "crawl_cached" in response_data
        assert "llm_cached" in response_data
        assert "processing_time" in response_data
        assert "sources" in response_data
        
        # Verify response content
        assert response_data["url"] == "https://example.com"
        assert response_data["query"] == "What is this page about and what does it contain?"
        assert response_data["response"] == "Based on the content, here is the answer to your query."
        assert response_data["crawl_cached"] == False
        assert response_data["llm_cached"] == False
        
        # Verify services were called
        mock_crawl.assert_called_once_with("https://example.com", use_cache=True)
        mock_llm_provider_instance.generate_content.assert_called_once()
        mock_history_service_instance.add_turn.assert_any_call("test_user", "What is this page about and what does it contain?", "user")
        mock_history_service_instance.add_turn.assert_any_call("test_user", "Based on the content, here is the answer to your query.", "assistant")
