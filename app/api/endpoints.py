from fastapi import APIRouter, Depends
from app.services.crawler import CrawlerService
from app.services.llm_provider import LLMProvider
from app.services.history import HistoryService
from app.services.caching import GPTCacheService
from app.schemas.models import (
    CrawlRequest,
    CrawlResponse,
    GenerateRequest,
    GenerateResponse,
    AddChatTurnRequest,
    GetChatHistoryResponse,
)
from app.core.config import Settings

router = APIRouter()

def get_settings():
    return Settings()

def get_llm_provider(settings: Settings = Depends(get_settings)):
    return LLMProvider(settings)

def get_history_service(settings: Settings = Depends(get_settings)):
    return HistoryService(settings)

def get_gptcache_service(settings: Settings = Depends(get_settings)):
    return GPTCacheService(settings)

@router.post("/crawl", response_model=CrawlResponse)
async def crawl(
    request: CrawlRequest, crawler: CrawlerService = Depends(CrawlerService)
):
    markdown = await crawler.crawl(request.url)
    return CrawlResponse(markdown=markdown)


@router.post("/generate", response_model=GenerateResponse)
async def generate(
    request: GenerateRequest, 
    cache: GPTCacheService = Depends(get_gptcache_service), # Add this dependency
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    # This logic explicitly controls caching
    cached_response = cache.get(request.prompt)
    if cached_response:
        return GenerateResponse(text=cached_response)

    text = await llm_provider.generate_content(request.prompt)
    cache.set(request.prompt, text)
    return GenerateResponse(text=text)


@router.post("/history/add")
async def add_chat_turn(
    request: AddChatTurnRequest, history_service: HistoryService = Depends(get_history_service)
):
    await history_service.add_turn(request.user_id, request.message, request.role)
    return {"message": "Chat turn added successfully."}


@router.get("/history/get/{user_id}", response_model=GetChatHistoryResponse)
async def get_chat_history(
    user_id: str, history_service: HistoryService = Depends(get_history_service)
):
    history = await history_service.get_history(user_id)
    return GetChatHistoryResponse(history=history)