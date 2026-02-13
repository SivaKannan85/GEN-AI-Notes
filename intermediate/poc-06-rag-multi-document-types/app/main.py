"""Main FastAPI application for POC 6 multi-document-type RAG."""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.document_processor import get_document_processor
from app.models import (
    AskRequest,
    AskResponse,
    ErrorResponse,
    HealthResponse,
    SourceDocument,
    UploadDocumentsRequest,
    UploadDocumentsResponse,
    VectorStoreInfo,
)
from app.qa_chain import get_qa_chain
from app.vectorstore_manager import get_vectorstore_manager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application dependencies and cleanup resources."""
    logger.info("Initializing POC 6 RAG service...")
    try:
        vectorstore_manager = get_vectorstore_manager()
        get_qa_chain()
        logger.info("Vectorstore initialized: %s", vectorstore_manager.is_initialized())
    except Exception as exc:  # noqa: BLE001
        logger.exception("Startup failed: %s", exc)
        raise

    yield

    logger.info("Shutting down service")
    get_vectorstore_manager().save()


settings = get_settings()
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
)


def _build_metadata_filter(filters) -> dict:
    if not filters:
        return {}
    payload = filters.model_dump(exclude_none=True)
    if "document_type" in payload:
        payload["document_type"] = payload["document_type"].value
    return payload


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint returning health status."""
    vectorstore_manager = get_vectorstore_manager()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        vectorstore_initialized=vectorstore_manager.is_initialized(),
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return await root()


@app.post(
    "/documents/upload",
    response_model=UploadDocumentsResponse,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Documents"],
)
async def upload_documents(request: UploadDocumentsRequest):
    """Upload one or many documents, parse, chunk, and index them."""
    try:
        processor = get_document_processor()
        chunks = processor.process_uploads(request.documents)

        vectorstore_manager = get_vectorstore_manager()
        chunks_added = vectorstore_manager.add_documents(chunks)

        return UploadDocumentsResponse(
            message="Documents uploaded successfully",
            documents_received=len(request.documents),
            chunks_added=chunks_added,
            document_count=vectorstore_manager.get_document_count(),
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001
        logger.exception("Upload failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to upload documents") from exc


@app.post(
    "/ask",
    response_model=AskResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
    tags=["Question Answering"],
)
async def ask_question(request: AskRequest):
    """Ask a question over indexed documents with optional metadata filters."""
    try:
        metadata_filter = _build_metadata_filter(request.filters)
        qa_chain = get_qa_chain()
        result = qa_chain.answer_question(
            question=request.question,
            top_k=request.top_k,
            metadata_filter=metadata_filter or None,
        )

        source_documents = [
            SourceDocument(content=doc.page_content, metadata=doc.metadata)
            for doc in result["source_documents"]
        ]

        return AskResponse(
            question=request.question,
            answer=result["answer"],
            source_documents=source_documents,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except HTTPException:
        raise
    except Exception as exc:  # noqa: BLE001
        logger.exception("Question answering failed: %s", exc)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to answer question") from exc


@app.get("/vectorstore/info", response_model=VectorStoreInfo, tags=["Vector Store"])
async def get_vectorstore_info():
    """Return vector store metadata."""
    manager = get_vectorstore_manager()
    return VectorStoreInfo(
        document_count=manager.get_document_count(),
        is_initialized=manager.is_initialized(),
    )


@app.delete("/vectorstore/clear", tags=["Vector Store"])
async def clear_vectorstore():
    """Delete all indexed content from vector store."""
    manager = get_vectorstore_manager()
    manager.clear()
    return {"message": "Vector store cleared successfully"}


@app.exception_handler(Exception)
async def global_exception_handler(_, exc):
    """Fallback error handler."""
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
