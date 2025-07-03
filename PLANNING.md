# PLANNING.md: Cache-Augmented Generation (CAG) System

This document outlines the architecture, goals, style, and constraints for the CAG project, synthesizing the requirements from `INITIAL.md` and adhering to the development principles in `GEMINI.md`.

## 1. Project Goal & Core Feature

The primary objective is to implement a Cache-Augmented Generation (CAG) system. This system will integrate a web crawler (`crawl4ai`) with a large language model (`gemini-2.0-flash`) to create a dynamic information-retrieval and processing pipeline. It will feature high-speed caching for LLM responses and persistent chat history to enable fluid, context-aware conversations.

### Key Workflow:
1.  **Crawl:** Fetch clean, LLM-friendly markdown from a given URL using `crawl4ai`.
2.  **Process:** Use the `gemini-2.0-flash` model to process the content (e.g., summarize, answer questions).
3.  **Cache:** Store both the crawled data and the LLM output in a Redis-backed cache (`GPTCache`) for rapid retrieval.
4.  **Converse:** Maintain a persistent chat history in Redis to provide context for multi-turn dialogues.

## 2. Architecture & Design

The system will be a modular, asynchronous FastAPI application, designed for testability and scalability. We will use dependency injection to manage services, inspired by the patterns in `examples/agent/agent.py`.

### Core Components:

-   **API Layer (`app/api/endpoints.py`):** A FastAPI router that exposes endpoints for user interaction. It will handle incoming requests (URL, query) and orchestrate the workflow.
-   **Configuration (`app/core/config.py`):** Pydantic-based settings management to load environment variables (API keys, Redis URL) from a `.env` file, as per `GEMINI.md`.
-   **Crawling Service (`app/services/crawler.py`):** A dedicated module wrapping the `crawl4ai` library. It will be responsible for all web content extraction and configured for responsible crawling (respecting `robots.txt`, setting user-agents).
-   **LLM Provider (`app/services/llm_provider.py`):** Manages all interactions with the Google Gemini API, specifically using the `gemini-2.0-flash` model. The design will follow the provider pattern seen in `examples/agent/providers.py`.
-   **Caching Service (`app/services/caching.py`):** Implements the caching logic using `GPTCache` with Redis as the backend. It will manage the cache for LLM responses.
-   **Chat History Service (`app/services/history.py`):** Manages the storage and retrieval of conversational history in Redis, using a distinct key schema to prevent collisions with the LLM cache.
-   **Data Schemas (`app/schemas/models.py`):** Pydantic models for API request/response validation and data structures.

## 3. File & Directory Structure

The project will adhere to the modular structure outlined in `GEMINI.md`.

```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── endpoints.py      # API routes and logic
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py         # Environment variables & settings
│   ├── services/
│   │   ├── __init__.py
│   │   ├── crawler.py        # crawl4ai service
│   │   ├── llm_provider.py   # Google Gemini service
│   │   ├── caching.py        # GPTCache service
│   │   └── history.py        # Chat history service
│   └── schemas/
│       ├── __init__.py
│       └── models.py         # Pydantic data models
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_services/
│       ├── __init__.py
│       ├── test_crawler.py
│       └── test_llm_provider.py
├── .env.example            # Example environment variables
├── cli.py                  # CLI for testing (inspired by examples/cli.py)
├── requirements.txt        # Project dependencies
├── vercel.json             # Vercel deployment configuration
├── GEMINI.md               # AI development guidelines
├── PLANNING.md             # This file
└── TASK.md                 # Task tracking
```

## 4. Style & Conventions

-   **Language:** Python, fully type-hinted.
-   **Formatting:** `black` and `PEP8` standards will be enforced.
-   **Docstrings:** Google-style docstrings for all functions and classes.
-   **Frameworks:**
    -   **API:** FastAPI
    -   **Data Validation:** Pydantic
    -   **ORM/Database:** Redis (direct or via libraries like `GPTCache`).
-   **Modularity:** No file will exceed 500 lines of code. Logic will be separated into modules as described above.
-   **Imports:** Relative imports will be preferred within the `app` package.

## 5. Testing & Reliability

-   **Framework:** `pytest` will be used for all unit tests.
-   **Scope:** New features (functions, classes, API routes) must have corresponding unit tests covering expected use, edge cases, and failure cases.
-   **Mocking:** External services (Google Gemini API, Redis, live websites for crawling) will be mocked to ensure isolated and reliable tests.
-   **Error Handling:** The application will implement robust error handling. Failures in the crawler or cache services should be logged and managed gracefully without crashing the application.

## 6. Constraints & Deployment

-   **LLM:** The system must exclusively use the `gemini-2.0-flash` model.
-   **Asynchronicity:** The entire codebase must be asynchronous (`async`/`await`).
-   **State Management:** Redis will serve as the backend for both the LLM response cache and chat history, using separate, clearly defined key schemas.
-   **Configuration:** All secrets (API keys, connection strings) must be managed via a `.env` file and `python-dotenv`. A `.env.example` file will be maintained.
-   **Deployment:** The application will be deployed on **Vercel**. A `vercel.json` file will be created to configure the serverless deployment, mapping the FastAPI application correctly.
