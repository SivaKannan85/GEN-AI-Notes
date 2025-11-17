"""
POC 6: RAG System with Multiple Document Types - Main Application

This FastAPI application implements a RAG system that supports multiple document
formats (PDF, TXT, DOCX, Markdown) with metadata filtering capabilities.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.models import (
    DocumentUploadResponse,
    QuestionRequest,
    QuestionResponse,
    DocumentType,
    HealthResponse,
    ErrorResponse,
    DocumentListResponse,
    DocumentStats,
)
from app.document_loaders import DocumentLoaderFactory, DocumentChunker
from app.vectorstore_manager import EnhancedVectorStoreManager
from app.qa_chain import MultiDocumentQAChain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Global instances
vectorstore_manager: Optional[EnhancedVectorStoreManager] = None
qa_chain: Optional[MultiDocumentQAChain] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global vectorstore_manager, qa_chain

    # Startup
    logger.info("Starting POC 6: RAG System with Multiple Document Types")

    # Create necessary directories
    os.makedirs(settings.upload_directory, exist_ok=True)
    os.makedirs(settings.vectorstore_path, exist_ok=True)

    # Initialize vectorstore manager
    vectorstore_manager = EnhancedVectorStoreManager(
        persist_directory=settings.vectorstore_path,
        openai_api_key=settings.openai_api_key,
        embedding_model=settings.openai_embedding_model,
    )

    # Initialize QA chain
    qa_chain = MultiDocumentQAChain(
        vectorstore_manager=vectorstore_manager,
        openai_api_key=settings.openai_api_key,
        model_name=settings.openai_model,
        temperature=settings.openai_temperature,
    )

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI app
app = FastAPI(
    title="POC 6: RAG System with Multiple Document Types",
    description="Multi-format document RAG system with metadata filtering",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    return HealthResponse(
        status="healthy",
        message="POC 6: RAG System with Multiple Document Types is running",
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        # Check if vectorstore is initialized
        if vectorstore_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vectorstore not initialized"
            )

        return HealthResponse(
            status="healthy",
            message="All systems operational",
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: str = "recursive"
):
    """
    Upload and process a document (PDF, TXT, DOCX, or Markdown)

    Args:
        file: The document file to upload
        chunking_strategy: Strategy for splitting document (recursive, sentence, character)

    Returns:
        DocumentUploadResponse with document metadata
    """
    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.supported_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Supported types: {settings.supported_extensions}"
            )

        # Map extension to DocumentType
        extension_to_type = {
            ".pdf": DocumentType.PDF,
            ".txt": DocumentType.TXT,
            ".docx": DocumentType.DOCX,
            ".md": DocumentType.MARKDOWN,
        }
        document_type = extension_to_type[file_extension]

        # Save uploaded file
        file_path = os.path.join(settings.upload_directory, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Check file size
        file_size = os.path.getsize(file_path)
        if file_size > settings.max_file_size_mb * 1024 * 1024:
            os.remove(file_path)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of {settings.max_file_size_mb}MB"
            )

        logger.info(f"Processing document: {file.filename} (type: {document_type}, size: {file_size} bytes)")

        # Load document
        documents = DocumentLoaderFactory.load_document(file_path, document_type)

        # Chunk document
        chunker = DocumentChunker()
        chunks = chunker.chunk_documents(
            documents=documents,
            strategy=chunking_strategy,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        logger.info(f"Document split into {len(chunks)} chunks")

        # Add to vectorstore
        metadata = vectorstore_manager.add_documents(
            documents=chunks,
            filename=file.filename,
            file_type=document_type.value,
        )

        return DocumentUploadResponse(
            message=f"Document '{file.filename}' processed successfully",
            document_metadata=metadata,
            chunks_created=len(chunks),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    """
    Ask a question against the document collection

    Args:
        request: QuestionRequest with question and optional metadata filters

    Returns:
        QuestionResponse with answer and source documents
    """
    try:
        if qa_chain is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="QA chain not initialized"
            )

        logger.info(f"Processing question: {request.question[:100]}...")

        # Get answer
        response = qa_chain.ask(
            question=request.question,
            filter_metadata=request.filter_metadata,
            top_k=request.top_k,
        )

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error answering question: {str(e)}"
        )


@app.get("/documents", response_model=DocumentListResponse)
async def list_documents():
    """
    List all uploaded documents with their metadata

    Returns:
        DocumentListResponse with list of documents and statistics
    """
    try:
        if vectorstore_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vectorstore not initialized"
            )

        documents = vectorstore_manager.list_documents()
        stats = vectorstore_manager.get_document_stats()

        return DocumentListResponse(
            total_documents=len(documents),
            documents=documents,
            stats=stats,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )


@app.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document from the vectorstore

    Args:
        document_id: The ID of the document to delete

    Returns:
        Success message
    """
    try:
        if vectorstore_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vectorstore not initialized"
            )

        # Note: This is a simplified implementation
        # In production, you'd need to implement document deletion in the vectorstore manager
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Document deletion not yet implemented. This would require FAISS index rebuilding."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            detail=str(exc),
        ).dict(),
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
