import pytest
from unittest.mock import AsyncMock, patch
from app.services.llm_provider import LLMProvider


@pytest.mark.asyncio
@patch("google.generativeai.GenerativeModel.generate_content_async")
async def test_generate_content(mock_generate_content, settings):
    mock_generate_content.return_value = AsyncMock(text="test content")
    llm_provider = LLMProvider(settings)
    content = await llm_provider.generate_content("test prompt")
    assert content == "test content"
    mock_generate_content.assert_called_once_with("test prompt")