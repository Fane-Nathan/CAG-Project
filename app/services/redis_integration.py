"""
Redis Server Integration Service
Provides integration with the separate Redis server for advanced caching operations.
"""

import asyncio
import httpx
from typing import Optional, Dict, Any
from app.core.config import Settings


class RedisServerClient:
    """
    Client for communicating with the separate Redis server.
    """
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.base_url = settings.redis_server_url or "http://localhost:8001"
        self.enabled = settings.redis_server_enabled
        
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of the Redis server."""
        if not self.enabled:
            return {"status": "disabled", "message": "Redis server integration disabled"}
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/health/status")
                return response.json()
        except Exception as e:
            return {"status": "error", "message": f"Redis server unreachable: {e}"}
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics from Redis server."""
        if not self.enabled:
            return {}
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/cache/stats")
                return response.json()
        except Exception:
            return {}
    
    async def get_history_stats(self) -> Dict[str, Any]:
        """Get history statistics from Redis server."""
        if not self.enabled:
            return {}
            
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/history/stats")
                return response.json()
        except Exception:
            return {}
    
    async def clear_cache(self, pattern: Optional[str] = None) -> Dict[str, Any]:
        """Clear cache entries matching pattern."""
        if not self.enabled:
            return {"status": "disabled"}
            
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                params = {"pattern": pattern} if pattern else {}
                response = await client.delete(f"{self.base_url}/cache/clear", params=params)
                return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def backup_data(self) -> Dict[str, Any]:
        """Trigger a backup of Redis data."""
        if not self.enabled:
            return {"status": "disabled"}
            
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(f"{self.base_url}/admin/backup")
                return response.json()
        except Exception as e:
            return {"status": "error", "message": str(e)}