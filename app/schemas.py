from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500)


class ChatResponse(BaseModel):
    answer: str
    generated_sql: str
    data_preview: List[Dict]


class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
