"""
Pydantic models for RAG system with multiple document types.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    """Supported document types."""
    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    MARKDOWN = "markdown"
    MD = "md"


class ChunkingStrategy(str, Enum):
    """Document chunking strategies."""
    RECURSIVE = "recursive"
    CHARACTER = "character"
    TOKEN = "token"
    SEMANTIC = "semantic"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""
    filename: str = Field(..., description="Original filename")
    file_type: DocumentType = Field(..., description="Document type")
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow, description="Upload timestamp")
    file_size_bytes: int = Field(..., description="File size in bytes")
    page_count: Optional[int] = Field(None, description="Number of pages (for PDF)")
    category: Optional[str] = Field(None, description="Document category")
    tags: Optional[List[str]] = Field(default_factory=list, description="Document tags")
    custom_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Custom metadata")


class DocumentUploadResponse(BaseModel):
    """Response after document upload."""
    message: str = Field(..., description="Success message")
    document_metadata: DocumentMetadata = Field(..., description="Document metadata")
    chunks_created: int = Field(..., description="Number of chunks created")

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Document 'report.pdf' processed successfully",
                "document_metadata": {
                    "filename": "report.pdf",
                    "file_type": "pdf",
                    "upload_timestamp": "2024-01-15T10:30:00",
                    "file_size_bytes": 204800,
                    "page_count": 10
                },
                "chunks_created": 15
            }
        }


class QuestionRequest(BaseModel):
    """Request for asking questions."""
    question: str = Field(..., min_length=1, max_length=500, description="Question to ask")
    top_k: Optional[int] = Field(default=4, ge=1, le=20, description="Number of chunks to retrieve")
    filter_metadata: Optional[Dict[str, Any]] = Field(default=None, description="Metadata filters")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the key findings in the report?",
                "top_k": 4,
                "filter_metadata": {"category": "reports", "file_type": "pdf"}
            }
        }


class SourceDocument(BaseModel):
    """Source document information."""
    source: str = Field(..., description="Source document name")
    content: str = Field(..., description="Document content")
    metadata: Dict[str, Any] = Field(..., description="Document metadata")
    relevance_score: float = Field(..., description="Relevance score")

    class Config:
        json_schema_extra = {
            "example": {
                "source": "q4_report.pdf",
                "content": "The quarterly revenue increased by 15%...",
                "metadata": {
                    "filename": "q4_report.pdf",
                    "file_type": "pdf",
                    "page": 3
                },
                "relevance_score": 0.85
            }
        }


class QuestionResponse(BaseModel):
    """Response to a question."""
    question: str = Field(..., description="The question asked")
    answer: str = Field(..., description="Generated answer")
    sources: List[SourceDocument] = Field(..., description="Source documents used")
    total_sources: int = Field(..., description="Total number of sources")

    class Config:
        json_schema_extra = {
            "example": {
                "question": "What are the key findings?",
                "answer": "The key findings indicate...",
                "sources": [],
                "total_sources": 4
            }
        }


class DocumentInfo(BaseModel):
    """Information about a stored document."""
    document_id: str = Field(..., description="Document identifier")
    filename: str = Field(..., description="Filename")
    file_type: DocumentType = Field(..., description="Document type")
    chunk_count: int = Field(..., description="Number of chunks")
    metadata: DocumentMetadata = Field(..., description="Document metadata")


class DocumentStats(BaseModel):
    """Document statistics."""
    total_documents: int = Field(..., description="Total number of documents")
    documents_by_type: Dict[str, int] = Field(..., description="Count by document type")

    class Config:
        json_schema_extra = {
            "example": {
                "total_documents": 15,
                "documents_by_type": {"pdf": 8, "txt": 5, "docx": 2}
            }
        }


class DocumentListResponse(BaseModel):
    """Response listing documents."""
    total_documents: int = Field(..., description="Total number of documents")
    documents: List[DocumentMetadata] = Field(..., description="List of documents")
    stats: DocumentStats = Field(..., description="Document statistics")


class VectorStoreStats(BaseModel):
    """Vector store statistics."""
    total_chunks: int = Field(..., description="Total chunks in vectorstore")
    total_documents: int = Field(..., description="Total documents uploaded")
    documents_by_type: Dict[str, int] = Field(..., description="Document count by type")
    is_initialized: bool = Field(..., description="Whether vectorstore is initialized")

    class Config:
        json_schema_extra = {
            "example": {
                "total_chunks": 250,
                "total_documents": 15,
                "documents_by_type": {"pdf": 8, "txt": 5, "docx": 2},
                "is_initialized": True
            }
        }


class ChunkingConfig(BaseModel):
    """Configuration for document chunking."""
    strategy: ChunkingStrategy = Field(default=ChunkingStrategy.RECURSIVE, description="Chunking strategy")
    chunk_size: int = Field(default=1000, ge=100, le=4000, description="Chunk size in characters")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Overlap between chunks")

    class Config:
        json_schema_extra = {
            "example": {
                "strategy": "recursive",
                "chunk_size": 1000,
                "chunk_overlap": 200
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    message: str = Field(..., description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "message": "All systems operational"
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Unsupported file type",
                "detail": "Only PDF, TXT, DOCX, and Markdown files are supported"
            }
        }
