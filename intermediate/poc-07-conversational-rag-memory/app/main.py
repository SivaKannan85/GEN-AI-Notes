"""
POC 7: Conversational RAG with Memory - Main Application

This FastAPI application implements a conversational RAG system that combines
chat history with document retrieval for context-aware responses.
"""

import logging
import os
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, status, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

from app.config import get_settings
from app.models import (
    SessionCreateRequest,
    SessionCreateResponse,
    ChatRequest,
    ChatResponse,
    ConversationHistory,
    SessionListResponse,
    DocumentUploadResponse,
    HealthResponse,
    ErrorResponse,
    MessageRole,
)
from app.session_manager import SessionManager
from app.conversational_rag import ConversationalRAGChain
from app.document_loader import load_document, chunk_documents

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global settings
settings = get_settings()

# Global instances
session_manager: Optional[SessionManager] = None
rag_chain: Optional[ConversationalRAGChain] = None
vectorstore: Optional[FAISS] = None
embeddings: Optional[OpenAIEmbeddings] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources"""
    global session_manager, rag_chain, vectorstore, embeddings

    # Startup
    logger.info("Starting POC 7: Conversational RAG with Memory")

    # Create necessary directories
    os.makedirs(settings.upload_directory, exist_ok=True)
    os.makedirs(settings.vectorstore_path, exist_ok=True)

    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        model=settings.openai_embedding_model,
        openai_api_key=settings.openai_api_key,
    )

    # Initialize or load vectorstore
    vectorstore_file = os.path.join(settings.vectorstore_path, "index.faiss")
    if os.path.exists(vectorstore_file):
        try:
            vectorstore = FAISS.load_local(
                settings.vectorstore_path,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info("Loaded existing vectorstore")
        except Exception as e:
            logger.warning(f"Could not load vectorstore: {e}. Creating new one.")
            vectorstore = None
    else:
        vectorstore = None

    # Initialize session manager
    session_manager = SessionManager(
        max_history=settings.max_history_messages,
        session_timeout_minutes=settings.session_timeout_minutes,
    )

    # Initialize conversational RAG chain
    rag_chain = ConversationalRAGChain(
        vectorstore=vectorstore,
        openai_api_key=settings.openai_api_key,
        model_name=settings.openai_model,
        temperature=settings.openai_temperature,
        max_context_messages=settings.max_context_messages,
    )

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    if vectorstore:
        try:
            vectorstore.save_local(settings.vectorstore_path)
            logger.info("Saved vectorstore")
        except Exception as e:
            logger.error(f"Error saving vectorstore: {e}")


# Create FastAPI app
app = FastAPI(
    title="POC 7: Conversational RAG with Memory",
    description="Conversational RAG system with chat history and document retrieval",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint - health check"""
    active_sessions = session_manager.get_active_session_count() if session_manager else 0
    return HealthResponse(
        status="healthy",
        message="POC 7: Conversational RAG with Memory is running",
        active_sessions=active_sessions,
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        if session_manager is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Session manager not initialized"
            )

        active_sessions = session_manager.get_active_session_count()

        return HealthResponse(
            status="healthy",
            message="All systems operational",
            active_sessions=active_sessions,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Health check failed: {str(e)}"
        )


@app.post("/sessions", response_model=SessionCreateResponse)
async def create_session(request: SessionCreateRequest = SessionCreateRequest()):
    """
    Create a new conversation session.

    Args:
        request: Session creation request

    Returns:
        SessionCreateResponse with session ID
    """
    try:
        session = session_manager.create_session(
            session_name=request.session_name,
            metadata=request.metadata,
        )

        return SessionCreateResponse(
            session_id=session.session_id,
            session_name=session.session_name,
            created_at=session.created_at,
            message=f"Session '{session.session_id}' created successfully",
        )

    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating session: {str(e)}"
        )


@app.get("/sessions", response_model=SessionListResponse)
async def list_sessions():
    """
    List all active sessions.

    Returns:
        SessionListResponse with list of sessions
    """
    try:
        sessions = session_manager.list_sessions()

        return SessionListResponse(
            sessions=sessions,
            total_sessions=len(sessions),
        )

    except Exception as e:
        logger.error(f"Error listing sessions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing sessions: {str(e)}"
        )


@app.get("/sessions/{session_id}/history", response_model=ConversationHistory)
async def get_session_history(session_id: str):
    """
    Get conversation history for a session.

    Args:
        session_id: Session identifier

    Returns:
        ConversationHistory with all messages
    """
    try:
        session = session_manager.get_session(session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found or expired"
            )

        return session.get_conversation_history()

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting session history: {str(e)}"
        )


@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """
    Delete a conversation session.

    Args:
        session_id: Session identifier

    Returns:
        Success message
    """
    try:
        deleted = session_manager.delete_session(session_id)

        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{session_id}' not found"
            )

        return {"message": f"Session '{session_id}' deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting session: {str(e)}"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message in a conversation session.

    Args:
        request: Chat request with session_id and message

    Returns:
        ChatResponse with assistant's reply
    """
    try:
        # Get session
        session = session_manager.get_session(request.session_id)

        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session '{request.session_id}' not found or expired"
            )

        # Add user message to session
        session.add_message(MessageRole.USER, request.message)

        # Get response from RAG chain
        answer, sources, retrieval_used = rag_chain.ask(
            session=session,
            question=request.message,
            use_retrieval=request.use_retrieval,
            top_k=request.top_k,
            filter_metadata=request.filter_metadata,
        )

        # Add assistant message to session
        session.add_message(MessageRole.ASSISTANT, answer)

        return ChatResponse(
            session_id=session.session_id,
            message=answer,
            sources=sources,
            conversation_context_used=True,
            retrieval_used=retrieval_used,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat: {str(e)}"
        )


@app.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document for retrieval.

    Args:
        file: Document file to upload

    Returns:
        DocumentUploadResponse with processing details
    """
    global vectorstore, rag_chain

    try:
        # Validate file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in settings.supported_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Supported: {settings.supported_extensions}"
            )

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
                detail=f"File size exceeds maximum of {settings.max_file_size_mb}MB"
            )

        logger.info(f"Processing document: {file.filename}")

        # Load and chunk document
        documents = load_document(file_path)
        chunks = chunk_documents(
            documents=documents,
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap,
        )

        # Add to vectorstore
        if vectorstore is None:
            # Create new vectorstore
            vectorstore = FAISS.from_documents(chunks, embeddings)
            logger.info("Created new vectorstore")
        else:
            # Add to existing vectorstore
            vectorstore.add_documents(chunks)
            logger.info(f"Added {len(chunks)} chunks to vectorstore")

        # Update RAG chain with new vectorstore
        rag_chain.vectorstore = vectorstore

        # Save vectorstore
        vectorstore.save_local(settings.vectorstore_path)

        return DocumentUploadResponse(
            message=f"Document '{file.filename}' processed successfully",
            filename=file.filename,
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
