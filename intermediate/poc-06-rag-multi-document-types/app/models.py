"""Pydantic models for POC 6 multi-document-type RAG API."""
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator


class DocumentType(str, Enum):
    """Supported document types."""

    txt = "txt"
    md = "md"
    pdf = "pdf"
    docx = "docx"


class UploadDocumentRequest(BaseModel):
    """Upload request for a single document."""

    filename: str = Field(..., min_length=1, max_length=255)
    document_type: DocumentType
    content: Optional[str] = Field(default=None, description="Raw text content for txt/md, optionally pdf/docx")
    file_base64: Optional[str] = Field(default=None, description="Base64-encoded file payload (required for binary files unless content provided)")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_payload(self):
        if not self.content and not self.file_base64:
            raise ValueError("Either 'content' or 'file_base64' must be provided")
        return self


class UploadDocumentsRequest(BaseModel):
    """Batch upload request."""

    documents: List[UploadDocumentRequest] = Field(..., min_length=1, max_length=50)


class UploadDocumentsResponse(BaseModel):
    """Batch upload response."""

    message: str
    documents_received: int
    chunks_added: int
    document_count: int


class MetadataFilters(BaseModel):
    """Metadata filters for retrieval."""

    source: Optional[str] = None
    document_type: Optional[DocumentType] = None
    tags: Optional[List[str]] = None


class AskRequest(BaseModel):
    """Question request model."""

    question: str = Field(..., min_length=1, max_length=800)
    top_k: int = Field(default=4, ge=1, le=15)
    filters: Optional[MetadataFilters] = None


class SourceDocument(BaseModel):
    """Source document payload returned to client."""

    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AskResponse(BaseModel):
    """Question response model."""

    question: str
    answer: str
    source_documents: List[SourceDocument]


class VectorStoreInfo(BaseModel):
    """Vector store status and statistics."""

    document_count: int
    is_initialized: bool


class HealthResponse(BaseModel):
    """Health endpoint response."""

    status: str
    version: str
    vectorstore_initialized: bool


class ErrorResponse(BaseModel):
    """Standard API error payload."""

    error: str
    detail: Optional[str] = None
