"""
Main FastAPI application for LangChain chatbot.
POC 2: Simple LangChain Chatbot
"""
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import (
    ChatRequest,
    ChatResponse,
    ChatMessage,
    ClearSessionRequest,
    ClearSessionResponse,
    SessionInfo,
    HealthResponse,
    ErrorResponse
)
from app.chatbot import get_chatbot
from app.session_manager import get_session_manager

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
    logger.info("Initializing LangChain chatbot...")
    try:
        # Initialize chatbot (this also initializes session manager)
        chatbot = get_chatbot()
        logger.info("LangChain chatbot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")
    session_manager = get_session_manager()
    session_manager.clear_all_sessions()
    logger.info("All sessions cleared")


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
    session_manager = get_session_manager()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        active_sessions=session_manager.get_active_session_count()
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify service is running."""
    session_manager = get_session_manager()
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        active_sessions=session_manager.get_active_session_count()
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Chat"]
)
async def chat(request: ChatRequest):
    """
    Send a message to the chatbot and receive a response.
    Maintains conversation history per session.

    Args:
        request: ChatRequest containing session_id and message

    Returns:
        ChatResponse with assistant's response and conversation history

    Raises:
        HTTPException: On processing errors
    """
    try:
        logger.info(f"Chat request for session: {request.session_id}")

        # Get chatbot instance
        chatbot = get_chatbot()

        # Process the message
        result = chatbot.chat(
            session_id=request.session_id,
            message=request.message,
            temperature=request.temperature
        )

        # Convert history to ChatMessage objects with timestamps
        conversation_history = [
            ChatMessage(
                role=msg["role"],
                content=msg["content"],
                timestamp=msg.get("timestamp") or datetime.utcnow()
            )
            for msg in result["conversation_history"]
        ]

        return ChatResponse(
            session_id=request.session_id,
            message=result["response"],
            conversation_history=conversation_history,
            tokens_used=result["tokens_used"]
        )

    except Exception as e:
        logger.error(f"Error processing chat request: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process chat request: {str(e)}"
        )


@app.get(
    "/session/{session_id}",
    response_model=SessionInfo,
    responses={
        404: {"model": ErrorResponse, "description": "Session Not Found"},
    },
    tags=["Session Management"]
)
async def get_session(session_id: str):
    """
    Get information about a specific session.

    Args:
        session_id: Session identifier

    Returns:
        SessionInfo with session details

    Raises:
        HTTPException: If session not found
    """
    session_manager = get_session_manager()
    session_info = session_manager.get_session_info(session_id)

    if session_info is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{session_id}' not found"
        )

    return session_info


@app.post(
    "/session/clear",
    response_model=ClearSessionResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Session Not Found"},
    },
    tags=["Session Management"]
)
async def clear_session(request: ClearSessionRequest):
    """
    Clear a specific session and its conversation history.

    Args:
        request: ClearSessionRequest containing session_id

    Returns:
        ClearSessionResponse confirming the session was cleared

    Raises:
        HTTPException: If session not found
    """
    session_manager = get_session_manager()
    success = session_manager.clear_session(request.session_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session '{request.session_id}' not found"
        )

    logger.info(f"Session cleared: {request.session_id}")
    return ClearSessionResponse(
        session_id=request.session_id,
        message="Session cleared successfully"
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
