from fastapi import APIRouter, Depends, HTTPException
import time
import logging
from urllib.parse import urlparse
from app.services.crawler import CrawlerService
from app.services.llm_provider import LLMProvider
from app.services.history import HistoryService
from app.services.simple_caching import SimpleCacheService
from app.schemas.models import (
    CrawlRequest,
    CrawlResponse,
    GenerateRequest,
    GenerateResponse,
    AddChatTurnRequest,
    GetChatHistoryResponse,
    CAGRequest,
    CAGResponse,
)
from app.core.validation import ValidatedCrawlRequest, ValidatedGenerateRequest, ValidatedCAGRequest
from app.core.monitoring import monitor, track_request
from app.core.config import Settings

router = APIRouter()
logger = logging.getLogger(__name__)

def get_settings():
    return Settings()

def get_llm_provider():
    return LLMProvider()

def get_history_service(settings: Settings = Depends(get_settings)):
    return HistoryService(settings)

def get_gptcache_service(settings: Settings = Depends(get_settings)):
    return SimpleCacheService(settings)

def get_crawler_service(cache: SimpleCacheService = Depends(get_gptcache_service)):
    return CrawlerService(cache_service=cache)

def validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF attacks."""
    try:
        parsed = urlparse(url)
        # Only allow http and https schemes
        if parsed.scheme not in ['http', 'https']:
            return False
        # Prevent localhost and private IP ranges
        hostname = parsed.hostname
        if not hostname:
            return False
        # Block localhost, private IPs, and internal domains
        blocked_hosts = ['localhost', '127.0.0.1', '0.0.0.0', '::1']
        if hostname.lower() in blocked_hosts:
            return False
        # Block private IP ranges (basic check)
        if hostname.startswith(('10.', '172.', '192.168.')):
            return False
        return True
    except Exception:
        return False

@router.post("/crawl", response_model=CrawlResponse)
@track_request("crawl")
async def crawl(
    request: CrawlRequest, 
    crawler: CrawlerService = Depends(get_crawler_service)
):
    # Validate URL to prevent SSRF attacks
    if not validate_url(request.url):
        logger.warning(f"Invalid or potentially dangerous URL blocked: {request.url}")
        raise HTTPException(status_code=400, detail="Invalid or unsafe URL provided")
    
    logger.info(f"Crawling URL: {request.url}")
    crawl_data = await crawler.crawl_with_metadata(request.url, use_cache=request.use_cache)
    
    # Record cache metrics
    if crawl_data.get("cached_at"):
        monitor.record_cache_hit("crawl")
    else:
        monitor.record_cache_miss("crawl")
    return CrawlResponse(
        markdown=crawl_data["markdown"],
        cached=crawl_data.get("cached_at") is not None,
        timestamp=crawl_data.get("timestamp")
    )


@router.post("/generate", response_model=GenerateResponse)
@track_request("generate")
async def generate(
    request: GenerateRequest, 
    cache: SimpleCacheService = Depends(get_gptcache_service),
    llm_provider: LLMProvider = Depends(get_llm_provider)
):
    # Check cache first if enabled
    cached_response = None
    if request.use_cache:
        cached_response = await cache.get_llm_response(request.prompt)
        if cached_response:
            monitor.record_cache_hit("llm")
    
    if cached_response:
        logger.info(f"Cache hit for LLM prompt: {request.prompt[:50]}...")
        return GenerateResponse(text=cached_response, cached=True)
    
    monitor.record_cache_miss("llm")

    # Generate new response
    text = await llm_provider.generate_content(request.prompt)
    
    # Cache the response
    await cache.set_llm_response(request.prompt, text)
    
    return GenerateResponse(text=text, cached=False)


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


@router.post("/cag", response_model=CAGResponse)
@track_request("cag")
async def cache_augmented_generation(
    request: CAGRequest,
    crawler: CrawlerService = Depends(get_crawler_service),
    cache: SimpleCacheService = Depends(get_gptcache_service),
    llm_provider: LLMProvider = Depends(get_llm_provider),
    history_service: HistoryService = Depends(get_history_service)
):
    """
    Unified Cache-Augmented Generation endpoint.
    
    This endpoint combines the full CAG workflow:
    1. Crawl the URL (with caching)
    2. Process the content with LLM (with caching)
    3. Optionally include chat history for context
    4. Return comprehensive response with metadata
    """
    # Validate URL to prevent SSRF attacks
    if not validate_url(request.url):
        logger.warning(f"Invalid or potentially dangerous URL blocked in CAG: {request.url}")
        raise HTTPException(status_code=400, detail="Invalid or unsafe URL provided")
    
    logger.info(f"Starting CAG workflow for URL: {request.url}")
    start_time = time.time()
    
    # Step 1: Crawl the website with caching
    crawl_data = await crawler.crawl_with_metadata(request.url, use_cache=request.use_cache)
    crawl_cached = crawl_data.get("cached_at") is not None
    
    # Step 2: Prepare the prompt
    base_prompt = f"""Based on the following content from {request.url}:

{crawl_data['markdown']}

User Query: {request.query}

Please provide a comprehensive answer based on the content above."""
    
    # Step 3: Include chat history if requested
    final_prompt = base_prompt
    if request.include_history and request.user_id:
        history = await history_service.get_history(request.user_id)
        if history:
            history_context = "\n".join([
                f"{turn['role']}: {turn['message']}" for turn in history[-5:]  # Last 5 turns
            ])
            final_prompt = f"""Previous conversation context:
{history_context}

{base_prompt}"""
    
    # Step 4: Generate response with caching
    llm_cached = False
    if request.use_cache:
        cached_response = await cache.get_llm_response(final_prompt)
        if cached_response:
            llm_response = cached_response
            llm_cached = True
        else:
            llm_response = await llm_provider.generate_content(final_prompt)
            await cache.set_llm_response(final_prompt, llm_response)
    else:
        llm_response = await llm_provider.generate_content(final_prompt)
    
    # Step 5: Save to history if user_id provided
    if request.user_id:
        await history_service.add_turn(request.user_id, request.query, "user")
        await history_service.add_turn(request.user_id, llm_response, "assistant")
    
    processing_time = time.time() - start_time
    
    return CAGResponse(
        response=llm_response,
        url=request.url,
        query=request.query,
        crawl_cached=crawl_cached,
        llm_cached=llm_cached,
        crawl_timestamp=crawl_data.get("timestamp"),
        processing_time=processing_time,
        sources={
            "title": crawl_data.get("title", ""),
            "status_code": crawl_data.get("status_code", 200),
            "success": crawl_data.get("success", True)
        }
    )
