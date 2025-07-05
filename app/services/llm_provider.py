import google.generativeai as genai
from app.core.config import Settings

def configure_genai(settings: Settings):
    genai.configure(api_key=settings.google_api_key)

class LLMProvider:
    """
    A provider for interacting with the Google Generative AI API.
    """

    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model_name)

    async def generate_content(self, prompt: str) -> str:
        """
        Generates content using the specified model.
        """
        response = await self.model.generate_content_async(prompt)
        return response.text
