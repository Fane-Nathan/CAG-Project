"""
Admin endpoints for system management and monitoring.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, Optional
from app.core.config import Settings, get_settings
from app.services.redis_integration import RedisServerClient
from app.services.caching import GPTCacheService
from app.services.history import HistoryService
from app.core.monitoring import monitor
import time
import os
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_redis_client(settings: Settings = Depends(get_settings)):
    return RedisServerClient(settings)

def get_cache_service(settings: Settings = Depends(get_settings)):
    return GPTCacheService(settings)

def get_history_service(settings: Settings = Depends(get_settings)):
    return HistoryService(settings)

@router.get("/health/detailed")
async def detailed_health_check(
    settings: Settings = Depends(get_settings),
    redis_client: RedisServerClient = Depends(get_redis_client)
):
    """
    Comprehensive health check including all system components.
    """
    health_data = {
        "timestamp": time.time(),
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "status": "healthy",
        "components": {}
    }
    
    # Check Redis Server
    redis_health = await redis_client.health_check()
    health_data["components"]["redis_server"] = redis_health
    
    # Check GPTCache data directory
    gptcache_status = {
        "status": "ok" if os.path.exists(settings.gptcache_data_dir) else "warning",
        "data_dir": settings.gptcache_data_dir,
        "exists": os.path.exists(settings.gptcache_data_dir)
    }
    health_data["components"]["gptcache"] = gptcache_status
    
    # Check environment variables
    env_status = {
        "status": "ok",
        "google_api_key_set": bool(settings.google_api_key),
        "redis_url_set": bool(settings.redis_url),
        "debug_mode": settings.debug
    }
    health_data["components"]["environment"] = env_status
    
    # Determine overall status
    component_statuses = [comp.get("status", "unknown") for comp in health_data["components"].values()]
    if "error" in component_statuses:
        health_data["status"] = "unhealthy"
    elif "warning" in component_statuses:
        health_data["status"] = "degraded"
    
    return health_data

@router.get("/stats/system")
async def get_system_stats(
    redis_client: RedisServerClient = Depends(get_redis_client),
    settings: Settings = Depends(get_settings)
):
    """
    Get comprehensive system statistics.
    """
    stats = {
        "timestamp": time.time(),
        "cache": {},
        "history": {},
        "configuration": {
            "gptcache_data_dir": settings.gptcache_data_dir,
            "redis_server_enabled": settings.redis_server_enabled,
            "debug": settings.debug
        }
    }
    
    # Get cache stats
    cache_stats = await redis_client.get_cache_stats()
    stats["cache"] = cache_stats
    
    # Get history stats
    history_stats = await redis_client.get_history_stats()
    stats["history"] = history_stats
    
    return stats

@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None,
    redis_client: RedisServerClient = Depends(get_redis_client)
):
    """
    Clear cache entries. Optionally specify a pattern to match.
    """
    result = await redis_client.clear_cache(pattern)
    return result

@router.post("/backup/create")
async def create_backup(
    redis_client: RedisServerClient = Depends(get_redis_client)
):
    """
    Create a backup of the Redis data.
    """
    result = await redis_client.backup_data()
    return result

@router.get("/config")
async def get_configuration(settings: Settings = Depends(get_settings)):
    """
    Get current system configuration (sensitive data excluded).
    """
    return {
        "app_name": settings.app_name,
        "app_version": settings.app_version,
        "debug": settings.debug,
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "redis_db": settings.redis_db,
        "gptcache_data_dir": settings.gptcache_data_dir,
        "gptcache_llm_prefix": settings.gptcache_llm_prefix,
        "gptcache_crawl_prefix": settings.gptcache_crawl_prefix,
        "redis_server_enabled": settings.redis_server_enabled,
        "google_api_key_configured": bool(settings.google_api_key)
    }

@router.post("/test/cag")
async def test_cag_pipeline(
    cache_service: GPTCacheService = Depends(get_cache_service),
    history_service: HistoryService = Depends(get_history_service)
):
    """
    Test the CAG pipeline with a simple example.
    """
    test_results = {
        "timestamp": time.time(),
        "tests": {}
    }
    
    # Test cache service
    try:
        test_key = f"test_key_{int(time.time())}"
        test_value = "test_value"
        
        await cache_service.set_llm_response(test_key, test_value)
        retrieved_value = await cache_service.get_llm_response(test_key)
        
        test_results["tests"]["cache"] = {
            "status": "pass" if retrieved_value == test_value else "fail",
            "details": f"Set and retrieved value: {retrieved_value == test_value}"
        }
    except Exception as e:
        test_results["tests"]["cache"] = {
            "status": "error",
            "details": str(e)
        }
    
    # Test history service
    try:
        test_user = f"test_user_{int(time.time())}"
        await history_service.add_turn(test_user, "test message", "user")
        history = await history_service.get_history(test_user)
        
        test_results["tests"]["history"] = {
            "status": "pass" if len(history) > 0 else "fail",
            "details": f"Added and retrieved history: {len(history)} entries"
        }
        
        # Clean up test data
        await history_service.clear_history(test_user)
    except Exception as e:
        test_results["tests"]["history"] = {
            "status": "error",
            "details": str(e)
        }
    
    return test_results

@router.get("/metrics")
async def get_application_metrics():
    """
    Get comprehensive application metrics and performance data.
    """
    logger.info("Application metrics requested")
    return monitor.get_metrics()

@router.post("/metrics/reset")
async def reset_application_metrics():
    """
    Reset application metrics (useful for testing and maintenance).
    """
    logger.warning("Application metrics reset requested")
    monitor.reset_metrics()
    return {"status": "success", "message": "Metrics reset successfully"}