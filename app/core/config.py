from pydantic_settings import BaseSettings, SettingsConfigDict
from redis import from_url
from pydantic import Field, model_validator
from typing import Optional
from dotenv import load_dotenv

class Settings(BaseSettings):
    # Core API Configuration
    google_api_key: str
    
    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0")
    redis_host: Optional[str] = Field(default=None)
    redis_port: Optional[int] = Field(default=None)
    redis_db: Optional[int] = Field(default=None)
    
    # GPTCache Configuration
    gptcache_data_dir: str = Field(default="gptcache_data")
    gptcache_llm_prefix: str = Field(default="gptcache_llm")
    gptcache_crawl_prefix: str = Field(default="gptcache_crawl")
    
    # Application Configuration
    app_name: str = Field(default="CAG System")
    app_version: str = Field(default="1.0.0")
    debug: bool = Field(default=False)
    
    # Redis Server Integration
    redis_server_enabled: bool = Field(default=False)
    redis_server_url: Optional[str] = Field(default=None)

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        case_sensitive=False
    )

    @model_validator(mode='after')
    def parse_redis_url(self) -> 'Settings':
        if self.redis_url:
            try:
                conn = from_url(self.redis_url)
                self.redis_host = conn.connection_pool.connection_kwargs.get("host")
                self.redis_port = conn.connection_pool.connection_kwargs.get("port")
                self.redis_db = conn.connection_pool.connection_kwargs.get("db")
            except Exception as e:
                raise ValueError(f"Invalid Redis URL: {e}") from e
        return self
    
    def get_redis_config(self) -> dict:
        """Get Redis configuration for services."""
        return {
            "host": self.redis_host,
            "port": self.redis_port,
            "db": self.redis_db,
            "url": self.redis_url
        }
    
    def get_gptcache_config(self) -> dict:
        """Get GPTCache configuration."""
        return {
            "data_dir": self.gptcache_data_dir,
            "llm_prefix": self.gptcache_llm_prefix,
            "crawl_prefix": self.gptcache_crawl_prefix
        }

def load_env():
    """Load environment variables from .env file."""
    load_dotenv()

def get_settings() -> Settings:
    """Get application settings instance."""
    return Settings()
