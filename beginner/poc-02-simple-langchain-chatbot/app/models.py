"""
Pydantic models for chatbot request/response validation.
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """Individual message in a conversation."""
    role: str = Field(..., description="Role of the message sender (user or assistant)")
    content: str = Field(..., description="Content of the message")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Message timestamp")


class ChatRequest(BaseModel):
    """Request model for chat."""
    session_id: str = Field(..., min_length=1, max_length=100, description="Unique session identifier")
    message: str = Field(..., min_length=1, max_length=4000, description="User message")
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "message": "Hello, what can you help me with?",
                "temperature": 0.7
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat."""
    session_id: str = Field(..., description="Session identifier")
    message: str = Field(..., description="Assistant's response")
    conversation_history: List[ChatMessage] = Field(..., description="Full conversation history")
    tokens_used: int = Field(..., description="Tokens used in this interaction")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "message": "I'm a helpful assistant. I can answer questions, help with tasks, and have conversations!",
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Hello, what can you help me with?",
                        "timestamp": "2024-01-01T12:00:00"
                    },
                    {
                        "role": "assistant",
                        "content": "I'm a helpful assistant...",
                        "timestamp": "2024-01-01T12:00:01"
                    }
                ],
                "tokens_used": 45
            }
        }


class SessionInfo(BaseModel):
    """Information about a chat session."""
    session_id: str = Field(..., description="Session identifier")
    message_count: int = Field(..., description="Number of messages in the session")
    created_at: datetime = Field(..., description="Session creation time")
    last_activity: datetime = Field(..., description="Last activity time")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "message_count": 10,
                "created_at": "2024-01-01T12:00:00",
                "last_activity": "2024-01-01T12:30:00"
            }
        }


class ClearSessionRequest(BaseModel):
    """Request to clear a session."""
    session_id: str = Field(..., min_length=1, max_length=100, description="Session identifier to clear")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1"
            }
        }


class ClearSessionResponse(BaseModel):
    """Response after clearing a session."""
    session_id: str = Field(..., description="Cleared session identifier")
    message: str = Field(..., description="Confirmation message")

    class Config:
        json_schema_extra = {
            "example": {
                "session_id": "user-123-session-1",
                "message": "Session cleared successfully"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    active_sessions: int = Field(..., description="Number of active sessions")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "active_sessions": 5
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Session not found",
                "detail": "The specified session ID does not exist"
            }
        }
