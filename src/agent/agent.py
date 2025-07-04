from src.llm.gemini_client import GeminiClient
from src.crawler.crawler import Crawler
from src.redis_client.redis_api_client import RedisApiClient


class AIAgent:
    """
    The main AI Agent that orchestrates interactions with the LLM and web crawler.
    """

    def __init__(self, redis_api_base_url: str = "http://localhost:8000"):
        self.redis_api_client = RedisApiClient(base_url=redis_api_base_url)
        self.gemini_client = GeminiClient(redis_api_client=self.redis_api_client)
        self.crawler = Crawler(redis_api_client=self.redis_api_client)

    async def process_query(self, query: str, user_id: str) -> str:
        """
        Processes a user query, potentially involving web crawling and LLM generation.
        """
        # Example: If query contains a URL, crawl it first
        if "http" in query or "https" in query:
            print(f"Crawling URL from query: {query}")
            crawled_content = await self.crawler.fetch_and_extract_markdown(query)
            if crawled_content:
                llm_prompt = f"Summarize the following content: {crawled_content}"
            else:
                llm_prompt = (
                    f"Could not crawl the URL. Please provide more context for: {query}"
                )
        else:
            llm_prompt = query

        response = await self.gemini_client.generate_content(
            llm_prompt, user_id=user_id
        )
        return response
