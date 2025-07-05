import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.services.caching import GPTCacheService
import json


@pytest.mark.asyncio
@patch("app.services.caching.Cache")
@patch("app.services.caching.manager_factory")
async def test_gptcache_service_llm_get_success(mock_manager_factory, mock_cache_class, settings):
    """Test successful LLM cache get operation"""
    mock_cache_instance = MagicMock()
    mock_cache_class.return_value = mock_cache_instance
    mock_cache_instance.get.return_value = "cached_llm_response"
    
    cache_service = GPTCacheService(settings)
    result = await cache_service.get_llm_response("test_prompt")
    
    assert result == "cached_llm_response"


@pytest.mark.asyncio
@patch("app.services.caching.Cache")
@patch("app.services.caching.manager_factory")
async def test_gptcache_service_llm_get_error(mock_manager_factory, mock_cache_class, settings):
    """Test LLM cache get operation with error"""
    mock_cache_instance = MagicMock()
    mock_cache_class.return_value = mock_cache_instance
    mock_cache_instance.get.side_effect = Exception("Cache error")
    
    cache_service = GPTCacheService(settings)
    result = await cache_service.get_llm_response("test_prompt")
    
    assert result is None  # Should return None on error


@pytest.mark.asyncio
@patch("app.services.caching.Cache")
@patch("app.services.caching.manager_factory")
async def test_gptcache_service_llm_set_success(mock_manager_factory, mock_cache_class, settings):
    """Test successful LLM cache set operation"""
    mock_cache_instance = MagicMock()
    mock_cache_class.return_value = mock_cache_instance
    
    cache_service = GPTCacheService(settings)
    await cache_service.set_llm_response("test_prompt", "test_response")
    
    # Verify put was called (exact call verification depends on GPTCache internals)
    assert mock_cache_instance.put.called


@pytest.mark.asyncio
@patch("app.services.caching.Cache")
@patch("app.services.caching.manager_factory")
async def test_gptcache_service_crawl_cache(mock_manager_factory, mock_cache_class, settings):
    """Test crawled data caching functionality"""
    mock_llm_cache = MagicMock()
    mock_crawl_cache = MagicMock()
    mock_cache_class.side_effect = [mock_llm_cache, mock_crawl_cache]
    
    # Mock crawl cache get
    test_data = {
        "url": "https://example.com",
        "markdown": "# Test Content",
        "timestamp": 1234567890,
        "title": "Test Page"
    }
    mock_crawl_cache.get.return_value = json.dumps(test_data)
    
    cache_service = GPTCacheService(settings)
    
    # Test get crawled data
    result = await cache_service.get_crawled_data("https://example.com")
    assert result == test_data
    
    # Test set crawled data
    await cache_service.set_crawled_data("https://example.com", test_data)
    assert mock_crawl_cache.put.called


@pytest.mark.asyncio
@patch("app.services.caching.Cache")
@patch("app.services.caching.manager_factory")
async def test_gptcache_service_backward_compatibility(mock_manager_factory, mock_cache_class, settings):
    """Test backward compatibility methods"""
    mock_cache_instance = MagicMock()
    mock_cache_class.return_value = mock_cache_instance
    mock_cache_instance.get.return_value = "cached_value"
    
    cache_service = GPTCacheService(settings)
    
    # Test backward compatibility get
    result = await cache_service.get("test_key")
    assert result == "cached_value"
    
    # Test backward compatibility set
    await cache_service.set("test_key", "test_value")
    assert mock_cache_instance.put.called