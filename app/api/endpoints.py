from fastapi import APIRouter, Depends
from app.services.crawler import CrawlerService
from app.services.llm_provider import llm_provider
from app.services.history import HistoryService
from app.schemas.models import (
    CrawlRequest,
    CrawlResponse,
    GenerateRequest,
    GenerateResponse,
    AddChatTurnRequest,
    GetChatHistoryResponse,
)

router = APIRouter()


@router.post("/crawl", response_model=CrawlResponse)
async def crawl(
    request: CrawlRequest, crawler: CrawlerService = Depends(CrawlerService)
):
    markdown = await crawler.crawl(request.url)
    return CrawlResponse(markdown=markdown)


@router.post("/generate", response_model=GenerateResponse)
async def generate(request: GenerateRequest):
    text = await llm_provider.generate_content(request.prompt)
    return GenerateResponse(text=text)


@router.post("/history/add")
async def add_chat_turn(
    request: AddChatTurnRequest, history_service: HistoryService = Depends(HistoryService)
):
    await history_service.add_turn(request.user_id, request.message, request.role)
    return {"message": "Chat turn added successfully."}


@router.get("/history/get/{user_id}", response_model=GetChatHistoryResponse)
async def get_chat_history(
    user_id: str, history_service: HistoryService = Depends(HistoryService)
):
    history = await history_service.get_history(user_id)
    return GetChatHistoryResponse(history=history)
