import pytest
from unittest.mock import AsyncMock, patch, ANY
from app.services.crawler import CrawlerService


@pytest.mark.asyncio
@patch("crawl4ai.async_webcrawler.AsyncWebCrawler.arun")
async def test_crawl(mock_run):
    mock_run.return_value = AsyncMock(markdown="test markdown")
    crawler = CrawlerService()
    markdown = await crawler.crawl("https://example.com")
    assert markdown == "test markdown"
    mock_run.assert_called_once_with("https://example.com", config=ANY)
