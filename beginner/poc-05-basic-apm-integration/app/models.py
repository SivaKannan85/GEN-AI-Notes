"""
Pydantic models for APM demonstration endpoints.
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime


class TaskRequest(BaseModel):
    """Request to create a task."""
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: Optional[str] = Field(None, max_length=1000, description="Task description")
    priority: Optional[str] = Field(default="medium", description="Task priority (low, medium, high)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Complete project documentation",
                "description": "Write comprehensive documentation for the project",
                "priority": "high"
            }
        }


class TaskResponse(BaseModel):
    """Response after creating a task."""
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title")
    description: Optional[str] = Field(None, description="Task description")
    priority: str = Field(..., description="Task priority")
    created_at: datetime = Field(..., description="Creation timestamp")
    processing_time_ms: float = Field(..., description="Time taken to process request in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "task-123",
                "title": "Complete project documentation",
                "description": "Write comprehensive documentation",
                "priority": "high",
                "created_at": "2024-01-15T10:30:00",
                "processing_time_ms": 45.2
            }
        }


class DataProcessingRequest(BaseModel):
    """Request for data processing simulation."""
    items: List[str] = Field(..., min_length=1, max_length=100, description="List of items to process")
    delay_ms: Optional[int] = Field(default=100, ge=0, le=5000, description="Simulated processing delay in ms")

    class Config:
        json_schema_extra = {
            "example": {
                "items": ["item1", "item2", "item3"],
                "delay_ms": 100
            }
        }


class DataProcessingResponse(BaseModel):
    """Response from data processing."""
    processed_count: int = Field(..., description="Number of items processed")
    total_time_ms: float = Field(..., description="Total processing time in milliseconds")
    items: List[str] = Field(..., description="Processed items")

    class Config:
        json_schema_extra = {
            "example": {
                "processed_count": 3,
                "total_time_ms": 305.7,
                "items": ["ITEM1", "ITEM2", "ITEM3"]
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    apm_enabled: bool = Field(..., description="Whether APM is enabled")
    timestamp: datetime = Field(..., description="Current timestamp")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "apm_enabled": True,
                "timestamp": "2024-01-15T10:30:00"
            }
        }


class MetricsResponse(BaseModel):
    """Response with application metrics."""
    total_requests: int = Field(..., description="Total number of requests processed")
    avg_response_time_ms: float = Field(..., description="Average response time in milliseconds")
    error_count: int = Field(..., description="Total number of errors")

    class Config:
        json_schema_extra = {
            "example": {
                "total_requests": 1250,
                "avg_response_time_ms": 125.5,
                "error_count": 3
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    trace_id: Optional[str] = Field(None, description="APM trace ID")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Processing failed",
                "detail": "Invalid data format",
                "trace_id": "abc123-def456"
            }
        }
