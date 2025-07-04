# Cache-Augmented Generation (CAG) System

This project implements a Cache-Augmented Generation (CAG) system that integrates a web crawler, a large language model, and a Redis-backed cache to provide a dynamic information retrieval and processing pipeline.

## Features

-   **Web Crawling:** Fetches and extracts clean, LLM-friendly markdown from a given URL.
-   **Content Generation:** Uses Google's `gemini-2.0-flash` model to process the crawled content.
-   **Caching:** Stores crawled data and LLM responses in a Redis-backed cache for rapid retrieval.
-   **Chat History:** Maintains a persistent chat history in Redis to provide context for multi-turn dialogues.

## Project Structure

The project is organized into two main components:

-   **`app`:** A FastAPI application that provides an API for interacting with the CAG system.
-   **`src`:** The core logic for the CAG system, including the web crawler, LLM provider, and caching and history services.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/your-repository.git
    ```
2.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Create a `.env` file:**
    ```bash
    cp .env.example .env
    ```
4.  **Update the `.env` file with your API keys and Redis URL.**

## Usage

1.  **Start the FastAPI server:**
    ```bash
    uvicorn app.main:app --reload
    ```
2.  **Use the CLI to interact with the system:**
    ```bash
    python cli.py
    ```

## Deployment

This project is configured for deployment on Vercel. To deploy the application, follow these steps:

1.  **Install the Vercel CLI:**
    ```bash
    npm install -g vercel
    ```
2.  **Deploy the application:**
    ```bash
    vercel
    ```

## Testing

To run the tests, use the following command:
```bash
pytest
```