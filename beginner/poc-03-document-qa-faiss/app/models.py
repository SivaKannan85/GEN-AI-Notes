"""
Pydantic models for document QA system.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class DocumentUpload(BaseModel):
    """Request model for uploading documents."""
    content: str = Field(..., min_length=1, description="Document content")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata for the document")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Python is a high-level programming language...",
                "metadata": {"source": "python_docs.txt", "category": "programming"}
            }
        }


class DocumentUploadResponse(BaseModel):
    """Response after uploading documents."""
    message: str = Field(..., description="Success message")
    document_count: int = Field(..., description="Number of documents in the vectorstore")
    chunks_added: int = Field(..., description="Number of chunks added")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Documents uploaded successfully",
                "document_count": 5,
                "chunks_added": 23
            }
        }


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., min_length=1, max_length=500, description="Question to ask")
    top_k: Optional[int] = Field(default=3, ge=1, le=10, description="Number of relevant chunks to retrieve")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Python?",
                "top_k": 3
            }
        }


class SourceDocument(BaseModel):
    """Source document information."""
    content: str = Field(..., description="Content of the source chunk")
    metadata: dict = Field(default_factory=dict, description="Document metadata")
    relevance_score: Optional[float] = Field(None, description="Relevance score")

    class Config:
        json_schema_extra = {
            "example": {
                "content": "Python is a high-level programming language...",
                "metadata": {"source": "python_docs.txt"},
                "relevance_score": 0.95
            }
        }


class QuestionResponse(BaseModel):
    """Response model for questions."""
    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="Generated answer")
    source_documents: List[SourceDocument] = Field(..., description="Source documents used")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is Python?",
                "answer": "Python is a high-level, interpreted programming language...",
                "source_documents": [
                    {
                        "content": "Python is a high-level programming language...",
                        "metadata": {"source": "python_docs.txt"},
                        "relevance_score": 0.95
                    }
                ]
            }
        }


class VectorStoreInfo(BaseModel):
    """Information about the vector store."""
    document_count: int = Field(..., description="Number of documents in the store")
    is_initialized: bool = Field(..., description="Whether the store is initialized")

    class Config:
        json_schema_extra = {
            "example": {
                "document_count": 10,
                "is_initialized": True
            }
        }


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    vectorstore_initialized: bool = Field(..., description="Whether vectorstore is ready")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "vectorstore_initialized": True
            }
        }


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "No documents found",
                "detail": "Please upload documents before asking questions"
            }
        }
