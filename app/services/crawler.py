from crawl4ai.async_webcrawler import AsyncWebCrawler


class CrawlerService:
    """
    A service for crawling websites and extracting content.
    """

    def __init__(self):
        self.crawler = AsyncWebCrawler()

    async def crawl(self, url: str) -> str:
        """
        Crawls a website and returns the content as markdown.
        """
        result = await self.crawler.arun(url=url)
        return result.markdown
