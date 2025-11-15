"""
Main FastAPI application with OpenAI integration.
POC 1: Basic FastAPI + OpenAI Integration
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from openai import OpenAI, OpenAIError, APIError, RateLimitError, APIConnectionError

from app.config import get_settings
from app.models import ChatRequest, ChatResponse, HealthResponse, ErrorResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global OpenAI client
openai_client: OpenAI = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    global openai_client
    settings = get_settings()

    logger.info("Initializing OpenAI client...")
    try:
        openai_client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=settings.openai_timeout
        )
        logger.info("OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {str(e)}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down application...")


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
    """
    Root endpoint - health check.
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify service is running.
    """
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )


@app.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        429: {"model": ErrorResponse, "description": "Rate Limit Exceeded"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Chat"]
)
async def chat_completion(request: ChatRequest):
    """
    Generate a chat completion using OpenAI.

    Args:
        request: ChatRequest containing the user message and optional parameters

    Returns:
        ChatResponse with the AI generated response and metadata

    Raises:
        HTTPException: On OpenAI API errors or validation failures
    """
    try:
        logger.info(f"Received chat request with message: {request.message[:50]}...")

        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": request.system_prompt},
            {"role": "user", "content": request.message}
        ]

        # Call OpenAI API
        logger.info(f"Calling OpenAI API with model: {settings.openai_model}")
        response = openai_client.chat.completions.create(
            model=settings.openai_model,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        # Extract response data
        assistant_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        finish_reason = response.choices[0].finish_reason

        logger.info(f"OpenAI response received. Tokens used: {tokens_used}")

        return ChatResponse(
            response=assistant_message,
            model=response.model,
            tokens_used=tokens_used,
            finish_reason=finish_reason
        )

    except RateLimitError as e:
        logger.error(f"Rate limit exceeded: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="OpenAI API rate limit exceeded. Please try again later."
        )

    except APIConnectionError as e:
        logger.error(f"API connection error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to OpenAI API. Please try again later."
        )

    except APIError as e:
        logger.error(f"OpenAI API error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"OpenAI API error: {str(e)}"
        )

    except OpenAIError as e:
        logger.error(f"OpenAI error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OpenAI error: {str(e)}"
        )

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred. Please try again later."
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for unhandled exceptions.
    """
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
