"""FastAPI app for POC 7 Conversational RAG with Memory."""
import logging

from fastapi import FastAPI, HTTPException, status

from app.config import get_settings
from app.document_processor import DocumentProcessor
from app.memory_manager import MemoryManager
from app.models import (
    ChatRequest,
    ChatResponse,
    DocumentIndexRequest,
    DocumentIndexResponse,
    ErrorResponse,
    HealthResponse,
    SessionCreateResponse,
    SessionInfoResponse,
)
from app.retrieval_chain import RetrievalChain
from app.vectorstore_manager import VectorStoreManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
settings = get_settings()

app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
)

memory_manager = MemoryManager(max_history_turns=settings.max_history_turns)
document_processor = DocumentProcessor(settings.chunk_size, settings.chunk_overlap)
vectorstore_manager = VectorStoreManager()
retrieval_chain = RetrievalChain()


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        vectorstore_initialized=vectorstore_manager.is_initialized(),
        sessions=memory_manager.session_count(),
    )


@app.post("/sessions", response_model=SessionCreateResponse, tags=["Sessions"])
async def create_session():
    session_id, created_at = memory_manager.create_session()
    return SessionCreateResponse(session_id=session_id, created_at=created_at)


@app.get("/sessions/{session_id}", response_model=SessionInfoResponse, tags=["Sessions"])
async def get_session(session_id: str):
    return SessionInfoResponse(
        session_id=session_id,
        exists=memory_manager.session_exists(session_id),
        message_count=memory_manager.get_message_count(session_id),
    )


@app.delete("/sessions/{session_id}", response_model=SessionInfoResponse, tags=["Sessions"])
async def delete_session(session_id: str):
    memory_manager.delete_session(session_id)
    return SessionInfoResponse(session_id=session_id, exists=False, message_count=0)


@app.post(
    "/documents/index",
    response_model=DocumentIndexResponse,
    tags=["Documents"],
    responses={400: {"model": ErrorResponse}},
)
async def index_documents(request: DocumentIndexRequest):
    chunks = document_processor.chunk_documents(request.documents)
    indexed = vectorstore_manager.add_documents(chunks)
    if indexed == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No chunks were indexed")

    return DocumentIndexResponse(
        message="Documents indexed successfully",
        chunks_indexed=indexed,
        total_chunks=vectorstore_manager.total_chunks(),
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
    tags=["Chat"],
    responses={400: {"model": ErrorResponse}},
)
async def chat(request: ChatRequest):
    if not vectorstore_manager.is_initialized():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No documents indexed. Please call /documents/index first.",
        )

    history = memory_manager.get_history(request.session_id)
    query = retrieval_chain.make_query(request.message, history)
    docs = vectorstore_manager.similarity_search(query, k=request.top_k)
    answer, citations = retrieval_chain.answer(request.message, history, docs)

    memory_manager.add_turn(request.session_id, request.message, answer)

    return ChatResponse(
        session_id=request.session_id,
        answer=answer,
        citations=citations,
        used_history_turns=min(len(history) // 2, settings.max_history_turns),
    )
