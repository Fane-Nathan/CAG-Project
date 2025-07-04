import pytest
from unittest.mock import AsyncMock, MagicMock
from app.main import app
from app.api.endpoints import (
    get_llm_provider,
    get_gptcache_service,
    get_history_service,
)
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator
from redis import from_url
from typing import Optional


# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class TestSettings(BaseSettings):
    google_api_key: str
    redis_url: str
    redis_host: Optional[str] = Field(default=None)
    redis_port: Optional[int] = Field(default=None)
    redis_db: Optional[int] = Field(default=None)

    model_config = SettingsConfigDict(env_file=os.path.join(PROJECT_ROOT, ".env.test"), env_file_encoding="utf-8")

    @model_validator(mode='after')
    def parse_redis_url(self):
        if self.redis_url:
            conn = from_url(self.redis_url)
            self.redis_host = conn.connection_pool.connection_kwargs.get("host")
            self.redis_port = conn.connection_pool.connection_kwargs.get("port")
            self.redis_db = conn.connection_pool.connection_kwargs.get("db")
        return self

@pytest.fixture(scope="session")
def settings():
    """
    Provides a Settings instance for tests, loading from .env.test.
    """
    return TestSettings()


@pytest.fixture
def override_dependencies():
    """
    Mocks application dependencies for API tests.
    """
    mock_llm_provider_instance = AsyncMock()
    mock_gptcache_service_instance = MagicMock()
    mock_history_service_instance = AsyncMock()

    app.dependency_overrides[get_llm_provider] = lambda: mock_llm_provider_instance
    app.dependency_overrides[get_gptcache_service] = lambda: mock_gptcache_service_instance
    app.dependency_overrides[get_history_service] = lambda: mock_history_service_instance

    yield mock_llm_provider_instance, mock_gptcache_service_instance, mock_history_service_instance

    # Clean up the overrides after the test
    app.dependency_overrides = {}

@pytest.fixture
def test_client(override_dependencies):
    """
    Provides a TestClient with mocked dependencies.
    """
    # The override_dependencies fixture has already set up the mocks
    # Now, create the TestClient
    from fastapi.testclient import TestClient
    with TestClient(app) as client:
        yield client