import asyncio
import time
import logging
import json
import hashlib
from typing import Optional, Dict, Any
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class SimpleCacheService:
    """
    Simple caching service using Redis directly without GPTCache.
    Works with standard Redis installation.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self.redis_client = None
        self._initialize_redis()
    
    def _initialize_redis(self):
        """Initialize Redis client."""
        try:
            self.redis_client = redis.from_url(
                self.settings.redis_url,
                decode_responses=True
            )
            logger.info("Redis client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Redis client: {e}")
            raise
    
    def _hash_key(self, key: str, prefix: str = "") -> str:
        """Create a hash for the key."""
        full_key = f"{prefix}:{key}" if prefix else key
        return hashlib.md5(full_key.encode()).hexdigest()
    
    async def get_llm_response(self, prompt: str) -> Optional[str]:
        """
        Get cached LLM response for a given prompt.
        
        Args:
            prompt: The input prompt to check cache for
            
        Returns:
            Cached response if found, None otherwise
        """
        try:
            key = self._hash_key(prompt, "llm")
            result = await self.redis_client.get(key)
            if result:
                data = json.loads(result)
                logger.info(f"LLM cache hit for prompt hash: {key[:8]}...")
                return data.get("response")
            return None
        except Exception as e:
            logger.error(f"Failed to get LLM response from cache: {e}")
            return None
    
    async def set_llm_response(self, prompt: str, response: str, ttl: int = 3600) -> None:
        """
        Cache an LLM response for a given prompt.
        
        Args:
            prompt: The input prompt
            response: The LLM response to cache
            ttl: Time to live in seconds (default: 1 hour)
        """
        try:
            key = self._hash_key(prompt, "llm")
            data = {
                "prompt": prompt,
                "response": response,
                "timestamp": time.time()
            }
            await self.redis_client.setex(key, ttl, json.dumps(data))
            logger.info(f"LLM response cached with key: {key[:8]}...")
        except Exception as e:
            logger.error(f"Failed to set LLM response in cache: {e}")
    
    async def get_crawled_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached crawled data for a given URL.
        
        Args:
            url: The URL to check cache for
            
        Returns:
            Cached crawled data if found, None otherwise
        """
        try:
            key = self._hash_key(url, "crawl")
            result = await self.redis_client.get(key)
            if result:
                data = json.loads(result)
                logger.info(f"Crawl cache hit for URL: {url}")
                return data
            return None
        except Exception as e:
            logger.error(f"Failed to get crawled data from cache: {e}")
            return None
    
    async def set_crawled_data(self, url: str, data: Dict[str, Any], ttl: int = 7200) -> None:
        """
        Cache crawled data for a given URL.
        
        Args:
            url: The URL that was crawled
            data: The crawled data to cache
            ttl: Time to live in seconds (default: 2 hours)
        """
        try:
            key = self._hash_key(url, "crawl")
            cache_data = {
                "url": url,
                "timestamp": data.get("timestamp"),
                "markdown": data.get("markdown"),
                "title": data.get("title", ""),
                "status_code": data.get("status_code"),
                "cached_at": time.time()
            }
            await self.redis_client.setex(key, ttl, json.dumps(cache_data))
            logger.info(f"Crawled data cached for URL: {url}")
        except Exception as e:
            logger.error(f"Failed to set crawled data in cache: {e}")
    
    # Backward compatibility methods
    async def get(self, key: str) -> Optional[str]:
        """Backward compatibility method for LLM response caching."""
        return await self.get_llm_response(key)
    
    async def set(self, key: str, value: str) -> None:
        """Backward compatibility method for LLM response caching."""
        await self.set_llm_response(key, value)
    
    async def close(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()