# PRP: Cache-Augmented Generation (CAG) System with FastAPI Redis Server and Next.js Frontend

## Feature Name: Cache-Augmented Generation (CAG) System with FastAPI Redis Server and Next.js Frontend

## Overview

This feature implements a comprehensive Cache-Augmented Generation (CAG) system, leveraging a web crawler and a dedicated FastAPI Redis server to provide dynamic, information-retrieval, and processing capabilities. The system will utilize Google's `gemini-2.0-flash` model as its core intelligence.

The primary workflow involves:
1.  A web crawling component (`crawl4ai`) to fetch and extract LLM-friendly markdown content from specified URLs.
2.  Processing of extracted content by the `gemini-2.0-flash` model for summarization, analysis, or query answering.
3.  Storage of LLM output and crawled data in a high-speed cache (Redis) for rapid retrieval.
4.  Persistent chat history management (Redis) to maintain conversational context for fluid, multi-turn dialogues.

A self-contained FastAPI application will run as a separate process, providing a dedicated API for the AI agent to interact with and manage its caching and history database (Redis). This server will be configured via `settings.json` and can be run locally for development or deployed to Vercel for production.

To provide a user-friendly interface and enable web analytics, a separate **Next.js frontend application** will be developed. This frontend will interact with the FastAPI backend and be deployed independently on Vercel.

Key functionalities of this server include:
-   Cache Management: Endpoints for storing, retrieving, and invalidating cached LLM responses and crawled data.
-   Chat History Management: Endpoints for logging, retrieving, and managing conversational turns and context.
-   Health Checks: API endpoints to monitor the status and availability of the Redis connection and the server itself.
-   Configuration: The server will read its Redis connection details and other operational parameters from a `settings.json` file, allowing for flexible deployment environments.

## Research Findings

### Codebase Analysis

*   **Existing Patterns:** The `examples/` directory provides valuable patterns for structuring the application:
    *   `examples/agent/providers.py`: Template for managing and configuring LLM providers. This pattern should be adapted for the Google Gemini client library.
    *   `examples/cli.py`: Demonstrates a robust structure for a command-line interface, including asynchronous operations and streaming output. This can inspire validation scripts and testing interfaces.
    *   `examples/agent/agent.py`: Excellent examples of dependency injection and tool registration, which will be crucial for structuring caching and crawling logic as clean, testable services.
*   **Conventions:** Adhere to the project's conventions as outlined in `PLANNING.md` and `GEMINI.md`, including:
    *   Python as the primary language.
    *   PEP8, type hints, and `black` formatting.
    *   `pydantic` for data validation.
    *   `FastAPI` for APIs.
    *   Pytest for unit tests.
    *   Google-style docstrings.
    *   `python-dotenv` for environment variables.
*   **Test Patterns:** Tests should live in a `/tests` folder mirroring the main app structure, including at least one test for expected use, one edge case, and one failure case. Mocking external services (Gemini API, Redis, live websites) is essential for isolated testing.

### External Research

*   **Web Framework (FastAPI):**
    *   Official Documentation: [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
    *   Key aspects: Asynchronous operations (`async/await`), Pydantic for request/response models, dependency injection, routing, middleware.
*   **Web Crawler Library (Crawl4AI):**
    *   GitHub Repository: [https://github.com/unclecode/crawl4ai](https://github.com/unclecode/crawl4ai)
    *   Official Docs: [https://docs.crawl4ai.com/](https://docs.crawl4ai.com/)
    *   Focus on: Respecting `robots.txt`, user-agent strings, request delays, extracting clean markdown.
*   **AI Agent Framework (Pydantic AI):**
    *   Documentation: [https://ai.pydantic.dev/](https://ai.pydantic.dev/)
    *   Relevant for: Data validation and structuring AI-related models.
*   **LLM Provider (Google Gemini API):**
    *   Python Client Library: [https://ai.google.dev/gemini-api/docs/libraries/python](https://ai.google.dev/gemini-api/docs/libraries/python)
    *   Gemini Model Information: [https://ai.google.dev/gemini-api/docs/models](https://ai.google.dev/gemini-api/docs/models)
    *   Specific model: `gemini-2.0-flash`.
*   **Caching & Chat History Technology (Redis):**
    *   Redis Official Documentation: [https://redis.io/docs/](https://redis.io/docs/)
    *   Python client for Redis (e.g., `redis-py`): [https://redis-py.readthedocs.io/en/stable/](https://redis-py.readthedocs.io/en/stable/)
    *   Key aspects: Asynchronous Redis client, distinct key schemas for cache and history, persistence.
*   **Specialized Caching Library (GPTCache):**
    *   GitHub Repository: [https://github.com/zilliztech/GPTCache](https://github.com/zilliztech/GPTCache)
    *   Consider integrating GPTCache for LLM response caching, as it's designed for this purpose and can integrate with Redis.
*   **Chat History Management (LangChain Concepts):**
    *   LangChain Chat History Concepts: [https://python.langchain.com/docs/concepts/chat_history/](https://python.langchain.com/docs/concepts/chat_history/)
    *   While not directly using LangChain, its concepts for managing chat history can inform the design of the Redis-based history.
*   **Deployment (Vercel):**
    *   Vercel documentation for Python/FastAPI deployments: [https://vercel.com/docs/runtimes#official-runtimes/python](https://vercel.com/docs/runtimes#official-runtimes/python)
    *   Serverless function patterns compatible with FastAPI on Vercel.
*   **Frontend Framework (Next.js):**
    *   Official Documentation: [https://nextjs.org/docs](https://nextjs.org/docs)
    *   Key aspects: React-based, server-side rendering (SSR), static site generation (SSG), API routes, optimized for Vercel.
*   **Vercel Web Analytics:**
    *   Official Documentation: [https://vercel.com/docs/analytics](https://vercel.com/docs/analytics)
    *   Focus on: Simple integration for visitor and page view tracking.

## Implementation Blueprint

The implementation will be structured to ensure modularity, testability, and adherence to project conventions.

### High-Level Architecture

```
+-------------------+       +-------------------+       +-------------------+
| Next.js Frontend  | <---> | FastAPI Redis API | <---> |       Redis       |
+-------------------+       +-------------------+       +-------------------+
        ^                           ^
        |                           |
        |                     +-------------------+
        +---------------------|    Web Crawler    |
                              +-------------------+
                                      ^
                                      |
                              +-------------------+
                              | Google Gemini API |
                              +-------------------+
```

### Detailed Tasks

1.  **Project Setup & Dependencies:**
    *   Create a new directory for the FastAPI Redis server (e.g., `src/redis_server/`).
    *   Initialize a new Python virtual environment within this directory.
    *   Install necessary dependencies: `fastapi`, `uvicorn`, `redis`, `python-dotenv`, `pydantic`, `crawl4ai`, `google-generativeai`, `GPTCache` (if used).
    *   Update `requirements.txt` at the project root.

2.  **FastAPI Redis Server Implementation (`src/redis_server/`):**
    *   **Configuration (`settings.py`, `settings.json`):**
        *   Define a `Settings` Pydantic model to load configuration from `settings.json` and environment variables (using `python-dotenv`).
        *   Include Redis connection details (host, port, password, DB), and potentially other server-specific settings.
        *   Create a `settings.json` example.
    *   **Redis Connection (`database.py`):**
        *   Implement an asynchronous Redis client connection (e.g., using `aioredis` or `redis-py` with `asyncio`).
        *   Handle connection pooling and graceful shutdown.
    *   **Cache Management Endpoints (`cache_routes.py`):**
        *   `POST /cache/set`: Store data in Redis (key, value, expiration).
        *   `GET /cache/get/{key}`: Retrieve data from Redis.
        *   `DELETE /cache/invalidate/{key}`: Invalidate/delete cache entry.
        *   Integrate `GPTCache` for LLM response caching, ensuring it uses Redis as its backend.
    *   **Chat History Management Endpoints (`history_routes.py`):
        *   `POST /history/add`: Add a new chat turn to a user's history (user ID, message, role, timestamp).
        *   `GET /history/get/{user_id}`: Retrieve full chat history for a user.
        *   `DELETE /history/clear/{user_id}`: Clear a user's chat history.
        *   Ensure distinct key schemas for cache and history in Redis.
    *   **Health Check Endpoints (`health_routes.py`):**
        *   `GET /health`: Basic server health check.
        *   `GET /health/redis`: Check Redis connection status.
    *   **Main Application (`main.py`):**
        *   Initialize FastAPI app.
        *   Include routers for cache, history, and health endpoints.
        *   Implement startup/shutdown events for Redis connection.

3.  **Web Crawler Integration (`src/crawler/`):**
    *   Create a `Crawler` class/module.
    *   Implement methods to fetch and extract markdown content using `crawl4ai`.
    *   Ensure `robots.txt` adherence, user-agent strings, and request delays.
    *   Integrate with the FastAPI Redis server to store crawled content in the cache.

4.  **Gemini Model Integration (`src/llm/`):**
    *   Create a `GeminiClient` class/module.
    *   Implement methods for interacting with the `gemini-2.0-flash` model.
    *   Handle summarization, analysis, and query answering.
    *   Integrate with the FastAPI Redis server to store LLM responses in the cache and retrieve context from chat history.
    *   Adapt the `examples/agent/providers.py` pattern.

5.  **AI Agent (CLI) Updates:**
    *   Modify the main AI agent to interact with the new FastAPI Redis server for caching and history.
    *   Update the agent's logic to use the web crawler for information retrieval.
    *   Adapt the `examples/cli.py` and `examples/agent/agent.py` patterns for tool registration and dependency injection.

6.  **Next.js Frontend Implementation (`frontend/`):**
    *   **Project Setup:** Scaffold a new Next.js project.
    *   **Basic UI:** Create a simple user interface with an input field and display area.
    *   **API Integration:** Implement client-side logic to call the FastAPI `/generate` endpoint.
    *   **Vercel Analytics:** Integrate Vercel Web Analytics for visitor and page view tracking.

7.  **Deployment Configuration (Vercel):**
    *   Create `vercel.json` at the project root for deploying the FastAPI application as a serverless function.
    *   Configure environment variables for Vercel deployment.
    *   Create a separate `vercel.json` within the `frontend/` directory for deploying the Next.js application.

8.  **Documentation Updates:**
    *   Update `README.md` with setup and running instructions for both the FastAPI server and the Next.js frontend.
    *   Add details about `settings.json` and `.env.example`.

### Error Handling Strategy

*   **Centralized Exception Handling:** Implement FastAPI exception handlers for common errors (e.g., `HTTPException`, `RequestValidationError`).
*   **Redis Connection Errors:** Graceful degradation or informative error messages if Redis is unavailable. Implement retry mechanisms where appropriate.
*   **Crawler Errors:** Log crawling failures (e.g., network issues, invalid URLs) and provide fallback mechanisms (e.g., return empty content, use cached data if available).
*   **LLM API Errors:** Handle rate limits, authentication errors, and other API-specific issues from the Gemini API.
*   **Logging:** Use Python's `logging` module for comprehensive logging of application flow, warnings, and errors.

## Validation Gates

The following commands must be executed to ensure code quality and correctness:

```bash
# Navigate to the FastAPI Redis server directory for linting and type checking
cd src/redis_server/

# Syntax/Style and Type Checking
ruff check --fix .
mypy .

# Unit Tests for FastAPI Redis Server
pytest tests/

# Navigate back to the project root for overall project checks
cd ../../

# Overall project linting and type checking (if applicable to the entire project)
ruff check --fix .
mypy .

# Overall project unit tests
pytest tests/
```

## Quality Checklist

- [ ] All necessary context included
- [ ] Validation gates are executable by AI
- [ ] References existing patterns
- [ ] Clear implementation path
- [ ] Error handling documented

## Confidence Score

8/10 (Confidence is high due to clear requirements, existing examples, and well-documented external libraries. Potential complexities lie in integrating GPTCache with Redis and ensuring seamless asynchronous operations across all components, as well as Vercel deployment specifics.)
