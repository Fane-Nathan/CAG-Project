import asyncio
from crawl4ai.async_webcrawler import AsyncWebCrawler
from src.redis_client.redis_api_client import RedisApiClient


class Crawler:
    """
    A web crawler class to fetch and extract markdown content from URLs.
    Integrates with crawl4ai and can store content in Redis cache.
    """

    def __init__(self, redis_api_client: RedisApiClient):
        self.crawler = AsyncWebCrawler()
        self.redis_api_client = redis_api_client

    async def fetch_and_extract_markdown(self, url: str) -> str | None:
        """
        Fetches content from a URL and extracts it as markdown.
        Respects robots.txt, uses appropriate user-agent, and handles request delays.
        """
        try:
            # Check cache first
            cached_content = await self.redis_api_client.get_cache(f"crawled:{url}")
            if cached_content:
                print(f"Returning cached content for {url}")
                return cached_content

            # crawl4ai handles robots.txt, user-agent, and delays internally
            result = await self.crawler.run(url)
            if result and result.markdown:
                # Store in cache
                await self.redis_api_client.set_cache(
                    f"crawled:{url}", result.markdown, expiration=3600
                )  # Cache for 1 hour
                return result.markdown
            return None
        except Exception as e:
            print(f"Error fetching and extracting markdown from {url}: {e}")
            return None


# Example usage (for testing purposes, not part of the main application flow)
async def main():
    # For testing, you might need to run the FastAPI server separately
    redis_client = RedisApiClient()
    crawler = Crawler(redis_client)
    markdown_content = await crawler.fetch_and_extract_markdown(
        "https://www.example.com"
    )
    if markdown_content:
        print("Successfully crawled and extracted markdown.")
        # print(markdown_content[:500]) # Print first 500 chars


if __name__ == "__main__":
    asyncio.run(main())
