"""
Main FastAPI application for Pydantic AI Response Structuring.
POC 4: Pydantic AI Response Structuring
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import (
    ExtractionRequest,
    ContactInfo,
    ContactExtractionResponse,
    Recipe,
    RecipeExtractionResponse,
    EventInfo,
    EventExtractionResponse,
    ProductInfo,
    ProductExtractionResponse,
    SentimentAnalysis,
    SentimentExtractionResponse,
    HealthResponse,
    ErrorResponse
)
from app.extraction_service import get_extraction_service

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
    logger.info("Initializing Pydantic AI Structuring service...")
    try:
        # Initialize extraction service
        extraction_service = get_extraction_service()
        logger.info("Extraction service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize service: {str(e)}")
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
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify service is running."""
    return HealthResponse(
        status="healthy",
        version=settings.api_version
    )


@app.post(
    "/extract/contact",
    response_model=ContactExtractionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Extraction"]
)
async def extract_contact_info(request: ExtractionRequest):
    """
    Extract contact information from text.
    Extracts names, emails, phone numbers, companies, and addresses.

    Args:
        request: Text to extract contact information from

    Returns:
        ContactExtractionResponse with extracted contact details

    Raises:
        HTTPException: On extraction errors
    """
    try:
        logger.info("Extracting contact information...")

        extraction_service = get_extraction_service()

        # Extract contact info
        contact, confidence = extraction_service.extract_with_confidence(
            text=request.text,
            model=ContactInfo,
            function_name="extract_contact_info",
            function_description="Extract contact information including name, email, phone, company, and address from text",
            system_prompt="You are an expert at extracting contact information from text. Extract all available contact details accurately."
        )

        return ContactExtractionResponse(
            contacts=[contact],
            confidence=confidence
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error extracting contact info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract contact information: {str(e)}"
        )


@app.post(
    "/extract/recipe",
    response_model=RecipeExtractionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Extraction"]
)
async def extract_recipe(request: ExtractionRequest):
    """
    Extract recipe information from text.
    Extracts title, ingredients, instructions, times, and servings.

    Args:
        request: Text containing recipe information

    Returns:
        RecipeExtractionResponse with structured recipe data

    Raises:
        HTTPException: On extraction errors
    """
    try:
        logger.info("Extracting recipe...")

        extraction_service = get_extraction_service()

        # Extract recipe
        recipe, confidence = extraction_service.extract_with_confidence(
            text=request.text,
            model=Recipe,
            function_name="extract_recipe",
            function_description="Extract recipe information including title, ingredients with quantities, step-by-step instructions, prep time, cook time, and servings",
            system_prompt="You are an expert at parsing recipes. Extract all recipe details in a structured format."
        )

        return RecipeExtractionResponse(
            recipe=recipe,
            confidence=confidence
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error extracting recipe: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract recipe: {str(e)}"
        )


@app.post(
    "/extract/event",
    response_model=EventExtractionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Extraction"]
)
async def extract_event_info(request: ExtractionRequest):
    """
    Extract event information from text.
    Extracts title, date, time, location, organizer, and attendees.

    Args:
        request: Text containing event information

    Returns:
        EventExtractionResponse with structured event data

    Raises:
        HTTPException: On extraction errors
    """
    try:
        logger.info("Extracting event information...")

        extraction_service = get_extraction_service()

        # Extract event info
        event, confidence = extraction_service.extract_with_confidence(
            text=request.text,
            model=EventInfo,
            function_name="extract_event_info",
            function_description="Extract event information including title, description, date, time, location, organizer, and attendees",
            system_prompt="You are an expert at extracting event details from text. Parse all event information accurately."
        )

        return EventExtractionResponse(
            events=[event],
            confidence=confidence
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error extracting event info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract event information: {str(e)}"
        )


@app.post(
    "/extract/product",
    response_model=ProductExtractionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Extraction"]
)
async def extract_product_info(request: ExtractionRequest):
    """
    Extract product information from text.
    Extracts name, category, price, brand, description, features, and specs.

    Args:
        request: Text containing product information

    Returns:
        ProductExtractionResponse with structured product data

    Raises:
        HTTPException: On extraction errors
    """
    try:
        logger.info("Extracting product information...")

        extraction_service = get_extraction_service()

        # Extract product info
        product, confidence = extraction_service.extract_with_confidence(
            text=request.text,
            model=ProductInfo,
            function_name="extract_product_info",
            function_description="Extract product information including name, category, price, brand, description, features, and specifications",
            system_prompt="You are an expert at extracting product details from descriptions. Parse all product information in a structured format."
        )

        return ProductExtractionResponse(
            products=[product],
            confidence=confidence
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error extracting product info: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to extract product information: {str(e)}"
        )


@app.post(
    "/extract/sentiment",
    response_model=SentimentExtractionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"model": ErrorResponse, "description": "Bad Request"},
        500: {"model": ErrorResponse, "description": "Internal Server Error"},
    },
    tags=["Extraction"]
)
async def extract_sentiment(request: ExtractionRequest):
    """
    Analyze sentiment from text.
    Extracts overall sentiment, positive/negative aspects, and summary.

    Args:
        request: Text to analyze sentiment from

    Returns:
        SentimentExtractionResponse with sentiment analysis

    Raises:
        HTTPException: On extraction errors
    """
    try:
        logger.info("Analyzing sentiment...")

        extraction_service = get_extraction_service()

        # Extract sentiment
        sentiment, confidence = extraction_service.extract_with_confidence(
            text=request.text,
            model=SentimentAnalysis,
            function_name="analyze_sentiment",
            function_description="Analyze sentiment from text, identifying overall sentiment (positive/negative/neutral/mixed), positive and negative aspects, and providing a summary",
            system_prompt="You are an expert at sentiment analysis. Accurately identify the overall sentiment and extract specific positive and negative aspects mentioned in the text."
        )

        return SentimentExtractionResponse(
            analysis=sentiment
        )

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error analyzing sentiment: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze sentiment: {str(e)}"
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
