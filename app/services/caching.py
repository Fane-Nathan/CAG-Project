import asyncio
import time
import logging
from typing import Optional, Dict, Any
from gptcache import Cache
from gptcache.manager import manager_factory
from gptcache.processor.pre import get_prompt
from gptcache.similarity_evaluation import ExactMatchEvaluation
import hashlib
import json

logger = logging.getLogger(__name__)


class GPTCacheService:
    """
    Enhanced caching service using GPTCache with Redis backend.
    Supports both LLM response caching and crawled data caching.
    """
    
    def __init__(self, settings):
        self.settings = settings
        self._llm_cache = None
        self._crawl_cache = None
        self._initialize_caches()
    
    def _initialize_caches(self):
        """Initialize GPTCache instances for LLM responses and crawled data."""
        # LLM Response Cache
        self._llm_cache = Cache()
        llm_data_manager = manager_factory(
            "redis,faiss",
            data_dir="gptcache_data/llm",
            scalar_params={
                "redis_host": self.settings.redis_host,
                "redis_port": self.settings.redis_port,
                "global_key_prefix": "gptcache_llm",
                **{k: v for k, v in {"db": self.settings.redis_db}.items() if v is not None}
            },
            vector_params={
                "dimension": 768,  # Default dimension for embeddings
            }
        )
        self._llm_cache.init(
            data_manager=llm_data_manager,
            pre_embedding_func=get_prompt,
            similarity_evaluation=ExactMatchEvaluation(),
        )
        
        # Crawled Data Cache (simpler, exact match only)
        self._crawl_cache = Cache()
        crawl_data_manager = manager_factory(
            "redis",
            scalar_params={
                "redis_host": self.settings.redis_host,
                "redis_port": self.settings.redis_port,
                "global_key_prefix": "gptcache_crawl",
                **{k: v for k, v in {"db": self.settings.redis_db}.items() if v is not None}
            }
        )
        self._crawl_cache.init(
            data_manager=crawl_data_manager,
            pre_embedding_func=lambda data, **kwargs: self._hash_url(data.get("url", "")),
            similarity_evaluation=ExactMatchEvaluation(),
        )
    
    def _hash_url(self, url: str) -> str:
        """Create a hash for URL-based caching."""
        return hashlib.md5(url.encode()).hexdigest()
    
    async def get_llm_response(self, prompt: str) -> Optional[str]:
        """
        Get cached LLM response for a given prompt.
        
        Args:
            prompt: The input prompt to check cache for
            
        Returns:
            Cached response if found, None otherwise
        """
        try:
            # Run in thread pool since GPTCache is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None, 
                lambda: self._llm_cache.get(prompt)
            )
            return result
        except Exception as e:
            logger.error(f"Failed to get LLM response from cache: {e}")
            return None
    
    async def set_llm_response(self, prompt: str, response: str) -> None:
        """
        Cache an LLM response for a given prompt.
        
        Args:
            prompt: The input prompt
            response: The LLM response to cache
        """
        try:
            # Run in thread pool since GPTCache is synchronous
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._llm_cache.put(prompt, response)
            )
        except Exception as e:
            logger.error(f"Failed to set LLM response in cache: {e}")
            pass
    
    async def get_crawled_data(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached crawled data for a given URL.
        
        Args:
            url: The URL to check cache for
            
        Returns:
            Cached crawled data if found, None otherwise
        """
        try:
            # Run in thread pool since GPTCache is synchronous
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._crawl_cache.get({"url": url})
            )
            if result:
                return json.loads(result)
            return None
        except Exception as e:
            logger.error(f"Failed to get crawled data from cache: {e}")
            return None
    
    async def set_crawled_data(self, url: str, data: Dict[str, Any]) -> None:
        """
        Cache crawled data for a given URL.
        
        Args:
            url: The URL that was crawled
            data: The crawled data to cache (should include 'markdown', 'timestamp', etc.)
        """
        try:
            # Add metadata
            cache_data = {
                "url": url,
                "timestamp": data.get("timestamp"),
                "markdown": data.get("markdown"),
                "title": data.get("title", ""),
                "cached_at": time.time()
            }
            
            # Run in thread pool since GPTCache is synchronous
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self._crawl_cache.put({"url": url}, json.dumps(cache_data))
            )
        except Exception as e:
            logger.error(f"Failed to set crawled data in cache: {e}")
            pass
    
    # Backward compatibility methods
    async def get(self, key: str) -> Optional[str]:
        """Backward compatibility method for LLM response caching."""
        return await self.get_llm_response(key)
    
    async def set(self, key: str, value: str) -> None:
        """Backward compatibility method for LLM response caching."""
        await self.set_llm_response(key, value)
