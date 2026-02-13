"""Pydantic models for POC 7 conversational RAG service."""
from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str
    indexed_documents: int


class IngestRequest(BaseModel):
    documents: list[str] = Field(..., min_length=1, description="Plain text documents to index")


class IngestResponse(BaseModel):
    message: str
    indexed_documents: int


class AskRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class AskResponse(BaseModel):
    session_id: str
    question: str
    answer: str
    context_used: list[str]
    chat_history_size: int
