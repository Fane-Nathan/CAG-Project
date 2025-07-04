from pydantic_settings import BaseSettings, SettingsConfigDict
from redis import from_url
from pydantic import Field, model_validator
from typing import Optional

class Settings(BaseSettings):
    google_api_key: str
    redis_url: str
    redis_host: Optional[str] = Field(default=None)
    redis_port: Optional[int] = Field(default=None)
    redis_db: Optional[int] = Field(default=None)

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @model_validator(mode='after')
    def parse_redis_url(self):
        if self.redis_url:
            conn = from_url(self.redis_url)
            self.redis_host = conn.connection_pool.connection_kwargs.get("host")
            self.redis_port = conn.connection_pool.connection_kwargs.get("port")
            self.redis_db = conn.connection_pool.connection_kwargs.get("db")
        return self
