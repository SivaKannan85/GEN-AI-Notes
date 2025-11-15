"""
Main FastAPI application with ElasticAPM integration.
POC 5: Basic APM Integration
"""
import logging
import time
import asyncio
import uuid
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM

from app.config import get_settings
from app.models import (
    TaskRequest,
    TaskResponse,
    DataProcessingRequest,
    DataProcessingResponse,
    HealthResponse,
    MetricsResponse,
    ErrorResponse
)
from app.apm_utils import (
    capture_span,
    set_custom_context,
    label_transaction,
    capture_exception,
    get_trace_id,
    get_metrics
)

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
    settings = get_settings()
    logger.info("Initializing APM-enabled FastAPI application...")
    logger.info(f"APM Enabled: {settings.elastic_apm_enabled}")
    logger.info(f"APM Service Name: {settings.elastic_apm_service_name}")
    logger.info(f"APM Server URL: {settings.elastic_apm_server_url}")

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

# Initialize ElasticAPM
if settings.elastic_apm_enabled:
    apm_config = {
        'SERVICE_NAME': settings.elastic_apm_service_name,
        'SERVER_URL': settings.elastic_apm_server_url,
        'ENVIRONMENT': settings.elastic_apm_environment,
        'CAPTURE_BODY': settings.apm_capture_body,
        'CAPTURE_HEADERS': settings.apm_capture_headers,
        'TRANSACTION_SAMPLE_RATE': settings.apm_transaction_sample_rate,
        'SPAN_FRAMES_MIN_DURATION': settings.apm_span_frames_min_duration,
    }

    if settings.elastic_apm_secret_token:
        apm_config['SECRET_TOKEN'] = settings.elastic_apm_secret_token

    apm = ElasticAPM(app, client=make_apm_client(apm_config))
    logger.info("ElasticAPM middleware initialized")
else:
    logger.warning("ElasticAPM is disabled")


# Middleware for tracking metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to track request metrics."""
    start_time = time.time()
    is_error = False

    try:
        response = await call_next(request)
        if response.status_code >= 400:
            is_error = True
        return response
    except Exception as e:
        is_error = True
        raise
    finally:
        # Record metrics
        processing_time_ms = (time.time() - start_time) * 1000
        get_metrics().record_request(processing_time_ms, is_error)


@app.get("/", response_model=HealthResponse, tags=["Health"])
async def root():
    """Root endpoint - health check."""
    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        apm_enabled=settings.elastic_apm_enabled,
        timestamp=datetime.utcnow()
    )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint to verify service is running."""
    # Add custom labels to this transaction
    label_transaction(endpoint="health", check_type="basic")

    return HealthResponse(
        status="healthy",
        version=settings.api_version,
        apm_enabled=settings.elastic_apm_enabled,
        timestamp=datetime.utcnow()
    )


@app.get("/metrics", response_model=MetricsResponse, tags=["Monitoring"])
async def get_application_metrics():
    """Get application metrics."""
    metrics = get_metrics().get_metrics()

    return MetricsResponse(
        total_requests=metrics["total_requests"],
        avg_response_time_ms=metrics["avg_response_time_ms"],
        error_count=metrics["error_count"]
    )


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Tasks"]
)
async def create_task(request: TaskRequest):
    """
    Create a new task (demonstrates APM tracing).

    This endpoint demonstrates:
    - Automatic transaction tracking
    - Custom spans
    - Custom context
    - Labels
    """
    start_time = time.time()

    # Add custom context for this transaction
    set_custom_context({
        "task_title": request.title,
        "task_priority": request.priority
    })

    # Add labels
    label_transaction(priority=request.priority, operation="create_task")

    # Simulate task creation with custom span
    task_id = await _create_task_in_database(request)

    # Simulate additional processing with another span
    await _send_task_notification(task_id, request.title)

    processing_time_ms = (time.time() - start_time) * 1000

    logger.info(f"Task created: {task_id}")

    return TaskResponse(
        id=task_id,
        title=request.title,
        description=request.description,
        priority=request.priority,
        created_at=datetime.utcnow(),
        processing_time_ms=round(processing_time_ms, 2)
    )


@capture_span("database.create_task", "db.create")
async def _create_task_in_database(request: TaskRequest) -> str:
    """
    Simulate creating a task in database.
    This will appear as a separate span in APM.
    """
    # Simulate database operation
    await asyncio.sleep(0.05)  # 50ms simulated DB latency
    task_id = f"task-{uuid.uuid4().hex[:8]}"
    return task_id


@capture_span("notification.send_task_created", "external.notification")
async def _send_task_notification(task_id: str, title: str):
    """
    Simulate sending a notification.
    This will appear as a separate span in APM.
    """
    # Simulate external API call
    await asyncio.sleep(0.03)  # 30ms simulated API latency
    logger.info(f"Notification sent for task: {task_id}")


@app.post(
    "/process",
    response_model=DataProcessingResponse,
    status_code=status.HTTP_200_OK,
    tags=["Processing"]
)
async def process_data(request: DataProcessingRequest):
    """
    Process data (demonstrates custom spans and performance monitoring).

    This endpoint demonstrates:
    - Multiple custom spans
    - Performance tracking
    - Batch processing monitoring
    """
    start_time = time.time()

    # Add context
    set_custom_context({
        "item_count": len(request.items),
        "delay_ms": request.delay_ms
    })

    # Process items
    processed_items = await _process_items_batch(request.items, request.delay_ms)

    total_time_ms = (time.time() - start_time) * 1000

    return DataProcessingResponse(
        processed_count=len(processed_items),
        total_time_ms=round(total_time_ms, 2),
        items=processed_items
    )


@capture_span("batch_processing", "app.processing")
async def _process_items_batch(items: list, delay_ms: int) -> list:
    """
    Process items in batch with custom span.
    """
    processed = []

    for item in items:
        processed_item = await _process_single_item(item, delay_ms)
        processed.append(processed_item)

    return processed


@capture_span("single_item_processing", "app.processing")
async def _process_single_item(item: str, delay_ms: int) -> str:
    """
    Process a single item with simulated delay.
    """
    # Simulate processing time
    await asyncio.sleep(delay_ms / 1000)
    return item.upper()


@app.get("/error/test", tags=["Error Testing"])
async def trigger_error():
    """
    Trigger an error for testing APM error tracking.

    This endpoint intentionally raises an exception to demonstrate
    how errors are captured and tracked in APM.
    """
    try:
        # Simulate an error
        raise ValueError("This is a test error for APM demonstration")
    except Exception as e:
        # Capture exception with custom data
        capture_exception(
            e,
            custom={"test": True, "endpoint": "error_test"},
            handled=False
        )
        logger.error(f"Test error triggered: {str(e)}")

        # Get trace ID for error correlation
        trace_id = get_trace_id()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=ErrorResponse(
                error="Test error triggered",
                detail=str(e),
                trace_id=trace_id
            ).dict()
        )


@app.get("/slow", tags=["Performance Testing"])
async def slow_endpoint():
    """
    Slow endpoint for testing performance monitoring.

    This endpoint has intentional delays to demonstrate
    performance tracking and span duration monitoring.
    """
    # Add label
    label_transaction(performance_test=True)

    # Simulate slow database query
    await _slow_database_query()

    # Simulate slow external API call
    await _slow_external_api_call()

    return {"message": "Slow operation completed", "trace_id": get_trace_id()}


@capture_span("slow_database_query", "db.query")
async def _slow_database_query():
    """Simulate a slow database query."""
    await asyncio.sleep(1.0)  # 1 second delay


@capture_span("slow_external_api", "external.http")
async def _slow_external_api_call():
    """Simulate a slow external API call."""
    await asyncio.sleep(0.5)  # 500ms delay


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler with APM integration."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    # Capture exception in APM
    capture_exception(exc, handled=True)

    # Get trace ID for error correlation
    trace_id = get_trace_id()

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "trace_id": trace_id
        }
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
