import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from src.redis_client.redis_api_client import RedisApiClient
from src.redis_server.settings import settings


class GeminiClient:
    """
    A client for interacting with the Google Gemini API (gemini-2.0-flash model).
    Handles summarization, analysis, and query answering, with caching and history integration.
    """

    def __init__(self, redis_api_client: RedisApiClient):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel("gemini-2.0-flash")
        self.redis_api_client = redis_api_client

    async def generate_content(self, prompt: str, user_id: str | None = None) -> str:
        """
        Generates content using the Gemini model, leveraging cache and chat history.
        """
        # Check cache first
        cache_key = f"gemini_cache:{hash(prompt)}"
        cached_response = await self.redis_api_client.get_cache(cache_key)
        if cached_response:
            return cached_response

        # Retrieve chat history if user_id is provided
        full_prompt = prompt
        if user_id:
            chat_history = await self.redis_api_client.get_chat_history(user_id)

            # Construct prompt with history (simple concatenation for now)
            history_str = "\n".join(
                [f"{turn['role']}: {turn['message']}" for turn in chat_history]
            )
            full_prompt = f"{history_str}\nUser: {prompt}"

        try:
            response = await self.model.generate_content_async(
                full_prompt,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                },
            )
            generated_text = response.text

            # Store in cache
            await self.redis_api_client.set_cache(
                cache_key, generated_text, expiration=3600
            )  # Cache for 1 hour

            # Add to chat history if user_id is provided
            if user_id:
                await self.redis_api_client.add_chat_turn(user_id, prompt, "user")
                await self.redis_api_client.add_chat_turn(
                    user_id, generated_text, "model"
                )

            return generated_text
        except Exception as e:
            print(f"Error generating content with Gemini: {e}")
            return f"Error: Could not generate content. {e}"


# Example usage (for testing purposes)
async def main():
    # Ensure GEMINI_API_KEY is set in your environment or .env file
    # os.environ["GEMINI_API_KEY"] = "YOUR_API_KEY"
    redis_client = RedisApiClient()
    client = GeminiClient(redis_client)
    response = await client.generate_content(
        "Tell me a short story about a brave knight.", user_id="test_user_1"
    )
    print(response)


if __name__ == "__main__":
    import asyncio

    # This is a placeholder. In a real application, you'd load this from .env or similar.
    # For testing, you might temporarily set it.
    # os.environ["GEMINI_API_KEY"] = "YOUR_GEMINI_API_KEY"
    asyncio.run(main())
