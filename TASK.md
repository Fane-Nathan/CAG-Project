# CAG System Task List - 2025-07-03

This document breaks down the implementation of the Cache-Augmented Generation (CAG) system into actionable tasks, derived from `INITIAL.md`.

## Phase 1: Project Setup & Foundation

- [x] **Task 1.1:** Create the project directory structure as defined in `PLANNING.md` (`app`, `tests`, and subdirectories).
- [x] **Task 1.2:** Create `requirements.txt` and add initial dependencies: `fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `crawl4ai`, `google-generativeai`, `gptcache`, `redis`.
- [x] **Task 1.3:** Create the `.env.example` file with placeholders for `GOOGLE_API_KEY` and `REDIS_URL`.
- [x] **Task 1.4:** Implement the basic FastAPI application setup in `app/main.py`.
- [x] **Task 1.5:** Implement Pydantic-based settings management in `app/core/config.py` to load environment variables.

## Phase 2: Core Service Implementation

- [x] **Task 2.1:** Implement the `CrawlerService` in `app/services/crawler.py`. It should wrap `crawl4ai` and include responsible crawling configurations.
- [x] **Task 2.2:** Implement the `LLMProvider` in `app/services/llm_provider.py` to interact with the `gemini-2.0-flash` model using the `google-generativeai` library.
- [x] **Task 2.3:** Implement the `CachingService` in `app/services/caching.py` using `GPTCache` with a Redis backend for LLM responses.
- [x] **Task 2.4:** Implement the `HistoryService` in `app/services/history.py` to manage persistent chat history in Redis, ensuring a distinct key schema from the cache.

## Phase 3: API Integration & Workflow

- [x] **Task 3.1:** Define Pydantic schemas for API requests (URL, query) and responses in `app/schemas/models.py`.
- [x] **Task 3.2:** Create the main API endpoint in `app/api/endpoints.py`.
- [x] **Task 3.3:** Inject and orchestrate the `CrawlerService`, `LLMProvider`, `CachingService`, and `HistoryService` within the API endpoint to create the full, asynchronous processing pipeline.

## Phase 4: Testing & Validation

- [x] **Task 4.1:** Create a `cli.py` inspired by `examples/cli.py` for interactive testing of the full pipeline.
- [x] **Task 4.2:** Write unit tests for the `CrawlerService` in `tests/test_services/test_crawler.py`, mocking website calls.
- [x] **Task 4.3:** Write unit tests for the `LLMProvider` in `tests/test_services/test_llm_provider.py`, mocking the Gemini API.
- [x] **Task 4.4:** Write unit tests for the `CachingService` and `HistoryService`, mocking the Redis connection.
- [x] **Task 4.5:** Write integration tests for the API endpoint in `tests/test_api.py`.

## Phase 5: Deployment & Documentation (Backend)

- [x] **Task 5.1:** Create the `vercel.json` configuration file for deploying the FastAPI application on Vercel.
- [x] **Task 5.2:** Update the project `README.md` with detailed setup instructions, API usage, and deployment steps.
- [x] **Task 5.3:** Review all code for clarity, add necessary inline comments, and ensure all functions have Google-style docstrings.

## Phase 6: Frontend Implementation (Next.js)

- [ ] **Task 6.1:** Scaffold a new Next.js project in a `frontend/` directory.
- [ ] **Task 6.2:** Create a basic user interface with an input field for prompts and a display area for generated text.
- [ ] **Task 6.3:** Implement client-side logic to send requests to the FastAPI `/generate` endpoint.
- [ ] **Task 6.4:** Integrate Vercel Web Analytics into the Next.js application.
- [ ] **Task 6.5:** Create a `vercel.json` within the `frontend/` directory for deploying the Next.js application.

## Discovered During Work

*(Use this section to add any new tasks or sub-tasks that are identified during the development process.)*
