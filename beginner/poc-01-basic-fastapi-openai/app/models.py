"""
Pydantic models for request/response validation.
"""
from typing import Optional, List
from pydantic import BaseModel, Field


class Message(BaseModel):
    """Individual message in a conversation."""
    role: str = Field(..., description="Role of the message sender (system, user, or assistant)")
    content: str = Field(..., description="Content of the message")


class ChatRequest(BaseModel):
    """Request model for chat completion."""
    message: str = Field(..., min_length=1, max_length=4000, description="User message to send to the AI")
    system_prompt: Optional[str] = Field(
        default="You are a helpful assistant.",
        description="System prompt to guide AI behavior"
    )
    temperature: Optional[float] = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Sampling temperature (0-2)"
    )
    max_tokens: Optional[int] = Field(
        default=500,
        ge=1,
        le=4000,
        description="Maximum tokens to generate"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "message": "What is FastAPI?",
                "system_prompt": "You are a helpful assistant.",
                "temperature": 0.7,
                "max_tokens": 500
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat completion."""
    response: str = Field(..., description="AI generated response")
    model: str = Field(..., description="Model used for generation")
    tokens_used: int = Field(..., description="Total tokens used in the request")
    finish_reason: str = Field(..., description="Reason the generation finished")

    class Config:
        json_schema_extra = {
            "example": {
                "response": "FastAPI is a modern, fast web framework for building APIs with Python.",
                "model": "gpt-3.5-turbo",
                "tokens_used": 45,
                "finish_reason": "stop"
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0"
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid API key",
                "detail": "The provided OpenAI API key is invalid or expired"
            }
        }
