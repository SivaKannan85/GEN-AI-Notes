"""
Pydantic models for Conversational RAG system with memory.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    """Message role types."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    """Individual chat message."""
    role: MessageRole = Field(..., description="Message role")
    content: str = Field(..., description="Message content")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "What was the Q4 revenue?",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        }


class SessionCreateRequest(BaseModel):
    """Request to create a new session."""
    session_name: Optional[str] = Field(None, description="Optional session name")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Session metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "session_name": "Q4 Analysis Discussion",
                "metadata": {"user_id": "user123", "department": "finance"}
            }
        }


class SessionCreateResponse(BaseModel):
    """Response after creating a session."""
    session_id: str = Field(..., description="Unique session identifier")
    session_name: Optional[str] = Field(None, description="Session name")
    created_at: datetime = Field(..., description="Session creation timestamp")
    message: str = Field(..., description="Success message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-abc123",
                "session_name": "Q4 Analysis Discussion",
                "created_at": "2024-01-15T10:30:00Z",
                "message": "Session created successfully"
            }
        }


class ChatRequest(BaseModel):
    """Request for chat interaction."""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., min_length=1, max_length=1000, description="User message")
    use_retrieval: bool = Field(default=True, description="Whether to use document retrieval")
    top_k: Optional[int] = Field(default=4, ge=1, le=10, description="Number of documents to retrieve")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters for retrieval")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-abc123",
                "message": "What was the revenue growth?",
                "use_retrieval": True,
                "top_k": 4,
                "filter_metadata": {"file_type": "pdf"}
            }
        }


class SourceDocument(BaseModel):
    """Source document used in response."""
    source: str = Field(..., description="Document source name")
    content: str = Field(..., description="Relevant content excerpt")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    relevance_score: float = Field(..., description="Relevance score")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "q4_report.pdf",
                "content": "Revenue increased by 23% year-over-year...",
                "metadata": {"file_type": "pdf", "page": 2},
                "relevance_score": 0.89
            }
        }


class ChatResponse(BaseModel):
    """Response for chat interaction."""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Assistant's response")
    sources: List[SourceDocument] = Field(default_factory=list, description="Source documents used")
    conversation_context_used: bool = Field(..., description="Whether conversation history was used")
    retrieval_used: bool = Field(..., description="Whether document retrieval was used")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Response timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-abc123",
                "message": "The revenue grew by 23% year-over-year, reaching $12.5 million in Q4 2024.",
                "sources": [],
                "conversation_context_used": True,
                "retrieval_used": True,
                "timestamp": "2024-01-15T10:30:05Z"
            }
        }


class ConversationHistory(BaseModel):
    """Conversation history for a session."""
    session_id: str = Field(..., description="Session identifier")
    messages: List[ChatMessage] = Field(..., description="List of messages")
    total_messages: int = Field(..., description="Total number of messages")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-abc123",
                "messages": [],
                "total_messages": 10
            }
        }


class SessionInfo(BaseModel):
    """Session information."""
    session_id: str = Field(..., description="Session identifier")
    session_name: Optional[str] = Field(None, description="Session name")
    created_at: datetime = Field(..., description="Creation timestamp")
    last_activity: datetime = Field(..., description="Last activity timestamp")
    message_count: int = Field(..., description="Number of messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Session metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "sess-abc123",
                "session_name": "Q4 Analysis Discussion",
                "created_at": "2024-01-15T10:30:00Z",
                "last_activity": "2024-01-15T11:00:00Z",
                "message_count": 15,
                "metadata": {}
            }
        }


class SessionListResponse(BaseModel):
    """Response listing all sessions."""
    sessions: List[SessionInfo] = Field(..., description="List of sessions")
    total_sessions: int = Field(..., description="Total number of sessions")

    class Config:
        json_schema_extra = {
            "example": {
                "sessions": [],
                "total_sessions": 5
            }
        }


class DocumentUploadRequest(BaseModel):
    """Request for document upload."""
    chunking_strategy: str = Field(default="recursive", description="Chunking strategy")

    class Config:
        json_schema_extra = {
            "example": {
                "chunking_strategy": "recursive"
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Uploaded filename")
    chunks_created: int = Field(..., description="Number of chunks created")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Document uploaded successfully",
                "filename": "report.pdf",
                "chunks_created": 15
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")
    active_sessions: int = Field(..., description="Number of active sessions")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All systems operational",
                "active_sessions": 3
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Session not found",
                "detail": "No session exists with the provided session_id"
            }
        }
