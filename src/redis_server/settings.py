from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
import os


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables or settings.json.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    redis_host: str = Field("localhost", description="Redis server host")
    redis_port: int = Field(6379, description="Redis server port")
    redis_password: str | None = Field(None, description="Redis server password")
    redis_db: int = Field(0, description="Redis database number for general use")
    redis_cache_db: int = Field(1, description="Redis database number for cache")
    redis_history_db: int = Field(
        2, description="Redis database number for chat history"
    )

    GEMINI_API_KEY: str = Field(..., description="Google Gemini API Key")


# Load settings
settings = Settings()  # type: ignore[call-arg]

# Create a .env.example file if it doesn't exist
env_example_path = os.path.join(os.path.dirname(__file__), ".env.example")
if not os.path.exists(env_example_path):
    with open(env_example_path, "w") as f:
        f.write(
            """# Example environment variables for src/redis_server/
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0
REDIS_CACHE_DB=1
REDIS_HISTORY_DB=2
GEMINI_API_KEY=your_gemini_api_key_here
"""
        )
