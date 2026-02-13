"""Pydantic models for POC 7 API contracts."""
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    vectorstore_initialized: bool
    sessions: int


class ErrorResponse(BaseModel):
    detail: str


class SessionCreateResponse(BaseModel):
    session_id: str
    created_at: datetime


class SessionInfoResponse(BaseModel):
    session_id: str
    exists: bool
    message_count: int


class DocumentInput(BaseModel):
    content: str = Field(..., min_length=1)
    source: str = Field(default="inline")
    metadata: dict[str, Any] = Field(default_factory=dict)


class DocumentIndexRequest(BaseModel):
    documents: list[DocumentInput] = Field(..., min_length=1)


class DocumentIndexResponse(BaseModel):
    message: str
    chunks_indexed: int
    total_chunks: int


class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class Citation(BaseModel):
    source: str
    chunk_id: str
    snippet: str


class ChatResponse(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation]
    used_history_turns: int
