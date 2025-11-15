"""
Main FastAPI application for Document QA system.
POC 3: Document QA with FAISS
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import (
    DocumentUpload,
    DocumentUploadResponse,
    QuestionRequest,
    QuestionResponse,
    SourceDocument,
    VectorStoreInfo,
    HealthResponse,
    ErrorResponse
)
from app.document_processor import get_document_processor
from app.vectorstore_manager import get_vectorstore_manager
from app.qa_chain import get_qa_chain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Initializing Document QA system...")
    try:
        # Initialize components (loads existing vectorstore if available)
        vectorstore_manager = get_vectorstore_manager()
        qa_chain = get_qa_chain()
        logger.info(f"Vectorstore initialized: {vectorstore_manager.is_initialized()}")
        logger.info("Document QA system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize system: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    # Save vectorstore on shutdown
    vectorstore_manager = get_vectorstore_manager()
    if vectorstore_manager.is_initialized():
        vectorstore_manager.save()
    logger.info("Application shutdown complete")


# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - health check."""
    vectorstore_manager = get_vectorstore_manager()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        vectorstore_initialized=vectorstore_manager.is_initialized()
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify service is running."""
    vectorstore_manager = get_vectorstore_manager()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        vectorstore_initialized=vectorstore_manager.is_initialized()
    )


@app.post(
    "/documents/upload",
    response_model=DocumentUploadResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Documents"]
)
async def upload_document(document: DocumentUpload):
    """
    Upload and process a document.
    The document will be split into chunks and added to the vector store.

    Args:
        document: DocumentUpload containing content and optional metadata

    Returns:
        DocumentUploadResponse with success information

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info("Uploading document...")

        # Get processors
        doc_processor = get_document_processor()
        vectorstore_manager = get_vectorstore_manager()

        # Process document into chunks
        chunks = doc_processor.process_text(
            content=document.content,
            metadata=document.metadata or {}
        )

        # Add to vectorstore
        chunks_added = vectorstore_manager.add_documents(chunks)

        # Get updated document count
        doc_count = vectorstore_manager.get_document_count()

        logger.info(f"Document uploaded: {chunks_added} chunks added, total documents: {doc_count}")

        return DocumentUploadResponse(
            message="Documents uploaded successfully",
            document_count=doc_count,
            chunks_added=chunks_added
        )

    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload document: {str(e)}"
        )


@app.post(
    "/ask",
    response_model=QuestionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "No documents uploaded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Question Answering"]
)
async def ask_question(request: QuestionRequest):
    """
    Ask a question about the uploaded documents.
    Uses RAG (Retrieval-Augmented Generation) to answer based on document content.

    Args:
        request: QuestionRequest containing the question and retrieval parameters

    Returns:
        QuestionResponse with answer and source documents

    Raises:
        HTTPException: If no documents are uploaded or on processing errors
    """
    try:
        logger.info(f"Received question: {request.question}")

        # Get QA chain
        qa_chain = get_qa_chain()

        # Check if vectorstore is initialized
        vectorstore_manager = get_vectorstore_manager()
        if not vectorstore_manager.is_initialized():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No documents uploaded. Please upload documents first."
            )

        # Get answer
        result = qa_chain.answer_question(
            question=request.question,
            top_k=request.top_k
        )

        # Format source documents
        source_documents = [
            SourceDocument(
                content=doc.page_content,
                metadata=doc.metadata,
                relevance_score=None  # FAISS returns distance, not similarity score
            )
            for doc in result["source_documents"]
        ]

        logger.info(f"Question answered with {len(source_documents)} source documents")

        return QuestionResponse(
            question=request.question,
            answer=result["answer"],
            source_documents=source_documents
        )

    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error answering question: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to answer question: {str(e)}"
        )


@app.get(
    "/vectorstore/info",
    response_model=VectorStoreInfo,
    tags=["Vector Store"]
)
async def get_vectorstore_info():
    """
    Get information about the vector store.

    Returns:
        VectorStoreInfo with store statistics
    """
    vectorstore_manager = get_vectorstore_manager()
    return VectorStoreInfo(
        document_count=vectorstore_manager.get_document_count(),
        is_initialized=vectorstore_manager.is_initialized()
    )


@app.delete(
    "/vectorstore/clear",
    status_code=status.HTTP_200_OK,
    tags=["Vector Store"]
)
async def clear_vectorstore():
    """
    Clear all documents from the vector store.

    Returns:
        Success message
    """
    try:
        logger.info("Clearing vectorstore...")
        vectorstore_manager = get_vectorstore_manager()
        vectorstore_manager.clear()
        logger.info("Vectorstore cleared successfully")
        return {"message": "Vector store cleared successfully"}
    except Exception as e:
        logger.error(f"Error clearing vectorstore: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear vectorstore: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )
