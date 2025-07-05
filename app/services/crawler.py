from crawl4ai.async_webcrawler import AsyncWebCrawler
from typing import Dict, Any, Optional
import time


class CrawlerService:
    """
    A service for crawling websites and extracting content with caching support.
    """

    def __init__(self, cache_service=None):
        self.crawler = AsyncWebCrawler()
        self.cache_service = cache_service

    async def crawl(self, url: str, use_cache: bool = True) -> str:
        """
        Crawls a website and returns the content as markdown.
        
        Args:
            url: The URL to crawl
            use_cache: Whether to use cached data if available
            
        Returns:
            Markdown content from the website
        """
        # Check cache first if enabled
        if use_cache and self.cache_service:
            cached_data = await self.cache_service.get_crawled_data(url)
            if cached_data:
                return cached_data.get("markdown", "")
        
        # Crawl the website
        result = await self.crawler.arun(url=url)
        markdown_content = result.markdown
        
        # Cache the result if cache service is available
        if self.cache_service:
            crawl_data = {
                "markdown": markdown_content,
                "title": getattr(result, 'title', '') or '',
                "timestamp": time.time(),
                "url": url
            }
            await self.cache_service.set_crawled_data(url, crawl_data)
        
        return markdown_content
    
    async def crawl_with_metadata(self, url: str, use_cache: bool = True) -> Dict[str, Any]:
        """
        Crawls a website and returns detailed metadata along with content.
        
        Args:
            url: The URL to crawl
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary containing markdown, title, timestamp, and other metadata
        """
        # Check cache first if enabled
        if use_cache and self.cache_service:
            cached_data = await self.cache_service.get_crawled_data(url)
            if cached_data:
                # Ensure cached_at field exists to indicate this was from cache
                if 'cached_at' not in cached_data:
                    cached_data['cached_at'] = time.time()
                return cached_data
        
        # Crawl the website
        result = await self.crawler.arun(url=url)
        
        crawl_data = {
            "url": url,
            "markdown": result.markdown,
            "title": getattr(result, 'title', '') or '',
            "timestamp": time.time(),
            "success": result.success if hasattr(result, 'success') else True,
            "status_code": getattr(result, 'status_code', 200)
            # Note: No 'cached_at' field for fresh data
        }
        
        # Cache the result if cache service is available
        if self.cache_service:
            await self.cache_service.set_crawled_data(url, crawl_data)
        
        return crawl_data
