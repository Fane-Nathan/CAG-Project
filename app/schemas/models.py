from pydantic import BaseModel
from typing import List, Dict, Any


class CrawlRequest(BaseModel):
    url: str


class CrawlResponse(BaseModel):
    markdown: str


class GenerateRequest(BaseModel):
    prompt: str


class GenerateResponse(BaseModel):
    text: str


class AddChatTurnRequest(BaseModel):
    user_id: str
    message: str
    role: str


class GetChatHistoryResponse(BaseModel):
    history: List[Dict[str, Any]]
