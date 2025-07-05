from pydantic import BaseModel
from typing import List, Dict, Any, Optional


class CrawlRequest(BaseModel):
    url: str
    use_cache: bool = True


class CrawlResponse(BaseModel):
    markdown: str
    cached: bool = False
    timestamp: Optional[float] = None


class GenerateRequest(BaseModel):
    prompt: str
    use_cache: bool = True


class GenerateResponse(BaseModel):
    text: str
    cached: bool = False


class AddChatTurnRequest(BaseModel):
    user_id: str
    message: str
    role: str


class GetChatHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]


class CAGRequest(BaseModel):
    """Cache-Augmented Generation request combining crawl + process workflow."""
    url: str
    query: str
    user_id: Optional[str] = None
    use_cache: bool = True
    include_history: bool = False


class CAGResponse(BaseModel):
    """Cache-Augmented Generation response with detailed metadata."""
    response: str
    url: str
    query: str
    crawl_cached: bool = False
    llm_cached: bool = False
    crawl_timestamp: Optional[float] = None
    processing_time: Optional[float] = None
    sources: Optional[Dict[str, Any]] = None
