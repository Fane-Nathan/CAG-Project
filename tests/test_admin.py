"""
Tests for admin endpoints.
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_detailed_health_check(test_client, override_dependencies):
    """Test the detailed health check endpoint."""
    with patch("app.api.admin.RedisServerClient") as mock_redis_client_class:
        mock_redis_client = AsyncMock()
        mock_redis_client_class.return_value = mock_redis_client
        mock_redis_client.health_check.return_value = {"status": "ok"}
        
        response = test_client.get("/admin/health/detailed")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "app_name" in data
        assert "app_version" in data
        assert "status" in data
        assert "components" in data


@pytest.mark.asyncio
async def test_get_system_stats(test_client, override_dependencies):
    """Test the system stats endpoint."""
    with patch("app.api.admin.RedisServerClient") as mock_redis_client_class:
        mock_redis_client = AsyncMock()
        mock_redis_client_class.return_value = mock_redis_client
        mock_redis_client.get_cache_stats.return_value = {"cache_hits": 100}
        mock_redis_client.get_history_stats.return_value = {"total_users": 10}
        
        response = test_client.get("/admin/stats/system")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "cache" in data
        assert "history" in data
        assert "configuration" in data


@pytest.mark.asyncio
async def test_get_configuration(test_client, override_dependencies):
    """Test the configuration endpoint."""
    response = test_client.get("/admin/config")
    
    assert response.status_code == 200
    data = response.json()
    assert "app_name" in data
    assert "app_version" in data
    assert "debug" in data
    assert "google_api_key_configured" in data
    # Ensure sensitive data is not exposed
    assert "google_api_key" not in data


@pytest.mark.asyncio
async def test_clear_cache(test_client, override_dependencies):
    """Test the cache clear endpoint."""
    with patch("app.api.admin.RedisServerClient") as mock_redis_client_class:
        mock_redis_client = AsyncMock()
        mock_redis_client_class.return_value = mock_redis_client
        mock_redis_client.clear_cache.return_value = {"status": "success", "cleared": 10}
        
        response = test_client.post("/admin/cache/clear")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_create_backup(test_client, override_dependencies):
    """Test the backup creation endpoint."""
    with patch("app.api.admin.RedisServerClient") as mock_redis_client_class:
        mock_redis_client = AsyncMock()
        mock_redis_client_class.return_value = mock_redis_client
        mock_redis_client.backup_data.return_value = {"status": "success", "backup_id": "backup_123"}
        
        response = test_client.post("/admin/backup/create")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data


@pytest.mark.asyncio
async def test_test_cag_pipeline(test_client, override_dependencies):
    """Test the CAG pipeline test endpoint."""
    mock_llm_provider, mock_cache_service, mock_history_service = override_dependencies
    
    # Mock the cache service methods
    mock_cache_service.set_llm_response = AsyncMock()
    mock_cache_service.get_llm_response = AsyncMock(return_value="test_value")
    
    # Mock the history service methods
    mock_history_service.add_turn = AsyncMock()
    mock_history_service.get_history = AsyncMock(return_value=[{"message": "test", "role": "user"}])
    mock_history_service.clear_history = AsyncMock()
    
    # Mock the GPTCacheService constructor to avoid Redis connection
    with patch("app.api.admin.GPTCacheService") as mock_gptcache_class:
        mock_gptcache_class.return_value = mock_cache_service
        
        response = test_client.post("/admin/test/cag")
        
        assert response.status_code == 200
        data = response.json()
        assert "timestamp" in data
        assert "tests" in data
        assert "cache" in data["tests"]
        assert "history" in data["tests"]