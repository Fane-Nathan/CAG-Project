from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    google_api_key: str
    redis_url: str

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


settings = Settings()
