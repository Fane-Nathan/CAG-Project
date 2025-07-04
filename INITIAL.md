## FEATURE: Cache-Augmented Generation (CAG) System with FastAPI Redis Server

This feature implements a comprehensive Cache-Augmented Generation (CAG) system, leveraging a web crawler and a dedicated FastAPI Redis server to provide dynamic, information-retrieval, and processing capabilities. The system will utilize Google's `gemini-2.0-flash` model as its core intelligence.

The primary workflow will be as follows:
1.  A web crawling component, built using the **`crawl4ai`** library, will fetch and extract clean, LLM-friendly markdown content from specified URLs.
2.  The extracted content will be processed by the **`gemini-2.0-flash`** model for summarization, analysis, or to answer specific user queries.
3.  The final output from the LLM, as well as the initial crawled data, will be stored in a high-speed cache to ensure rapid retrieval for subsequent identical or similar requests.
4.  **Persistent Chat History:** All interactions between the user and the AI will be logged and stored to maintain conversational context. This history will be used in subsequent prompts to enable fluid, multi-turn dialogues.

This feature combines real-time data acquisition, intelligent caching, and stateful conversation management to provide users with up-to-date, context-aware, and efficient AI-driven insights.

A self-contained FastAPI application will run as a separate process, providing a dedicated API for the AI agent to interact with and manage its caching and history database (Redis). This server will be configured via `settings.json` and can be run locally for development or deployed to Vercel for production.

Key functionalities of this server include:
-   **Cache Management:** Endpoints for storing, retrieving, and invalidating cached LLM responses and crawled data.
-   **Chat History Management:** Endpoints for logging, retrieving, and managing conversational turns and context.
-   **Health Checks:** API endpoints to monitor the status and availability of the Redis connection and the server itself.
-   **Configuration:** The server will read its Redis connection details and other operational parameters from a `settings.json` file, allowing for flexible deployment environments.

## EXAMPLES:

While the `examples/` folder contains a project for a multi-agent system, the patterns within are highly relevant and should be used as a guide for best practices:

-   **`examples/agent/providers.py`**: Use this as a template for how to manage and configure the LLM provider. This pattern should be adapted for the Google Gemini client library.
-   **`examples/cli.py`**: This file demonstrates a robust structure for a command-line interface, including handling of asynchronous operations and providing clear, streaming output. This should inspire the validation scripts and any potential testing interface for the CAG and crawling system.
-   **`examples/agent/agent.py`**: The dependency injection and tool registration patterns in this file are excellent examples of how to structure the caching and crawling logic as clean, testable services that can be injected where needed.

## DOCUMENTATION:

-   **Web Framework:**
    -   FastAPI Official Documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
-   **Web Crawler Library:**
    -   Crawl4AI GitHub Repository: [https://github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)
    -   Crawl4AI Official Docs: [https://docs.crawl4ai.com/](https://docs.crawl4ai.com/)
-   **AI Agent Framework:**
    -   Pydantic AI Documentation: [https://ai.pydantic.dev/](https://ai.pydantic.dev/)
-   **LLM Provider Documentation:**
    -   Google AI Python Client Library: [https://ai.google.dev/gemini-api/docs/libraries/python](https://ai.google.dev/gemini-api/docs/libraries/python)
    -   Gemini Model Information: [https://ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
-   **Caching & Chat History Technology:**
    -   **Specialized Caching Library:**
        -   GPTCache GitHub Repository: [https://github.com/zilliztech/GPTCache](https://github.com/zilliztech/GPTCache)
    -   **Database Backend (for Cache and History):**
        -   Redis Official Documentation: [https://redis.io/docs/](https://redis.io/docs/)
    -   **Chat History Management:**
        -   LangChain Chat History Concepts: [https://python.langchain.com/docs/concepts/chat_history/](https://python.langchain.com/docs/concepts/chat_history/)

## OTHER CONSIDERATIONS:

-   **Deployment Platform:** The application will be deployed to **Vercel**. The implementation plan should account for this, including any necessary configuration files (e.g., `vercel.json`) and serverless function patterns compatible with FastAPI.
-   **State Management:** The system must manage both the **LLM response cache** and the **user's chat history**. **Redis** should be used as the backend for both, but with distinct key schemas to avoid collisions.
-   **Model Specification:** The system must specifically use the **`gemini-2.0-flash`** model. All API calls and configurations should reflect this choice.
-   **Configuration Management:** The implementation must use `python-dotenv` and a `.env.example` file to manage environment variables for the **Google Gemini API Key** and the Redis connection URL. Hardcoding credentials is not acceptable, as stipulated in `CLAUDE.md`.
-   **Asynchronous Operations:** The entire pipeline, including crawling, LLM interaction, caching, and history management, must be fully asynchronous.
-   **Responsible Crawling:** The `crawl4ai` component should be configured to respect `robots.txt` and to include appropriate user-agent strings and request delays.
-   **Error Handling:** The system must be resilient. If the Redis cache or the web crawler fails, the system should log the error and have a clear fallback mechanism, preventing a crash.
-   **Testing:** Comprehensive unit tests are required using `pytest`. These tests should mock the external services (Gemini API, Redis, and live websites) to test the application logic in isolation.