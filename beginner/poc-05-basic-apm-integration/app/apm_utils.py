"""
Utilities for working with ElasticAPM.
"""
import logging
from typing import Optional, Dict, Any
from functools import wraps
import elasticapm

logger = logging.getLogger(__name__)


def capture_span(span_name: str, span_type: str = "app"):
    """
    Decorator to capture a function as an APM span.

    Args:
        span_name: Name of the span
        span_type: Type of span (app, db, cache, external, etc.)

    Usage:
        @capture_span("process_data", "app.processing")
        def process_data(items):
            # function code
            pass
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            client = elasticapm.get_client()
            if client:
                with elasticapm.capture_span(span_name, span_type=span_type):
                    return await func(*args, **kwargs)
            return await func(*args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            client = elasticapm.get_client()
            if client:
                with elasticapm.capture_span(span_name, span_type=span_type):
                    return func(*args, **kwargs)
            return func(*args, **kwargs)

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def set_custom_context(data: Dict[str, Any]):
    """
    Set custom context data for the current transaction.

    Args:
        data: Dictionary of custom context data
    """
    client = elasticapm.get_client()
    if client:
        elasticapm.set_custom_context(data)


def set_user_context(
    user_id: Optional[str] = None,
    username: Optional[str] = None,
    email: Optional[str] = None
):
    """
    Set user context for the current transaction.

    Args:
        user_id: User ID
        username: Username
        email: User email
    """
    client = elasticapm.get_client()
    if client:
        elasticapm.set_user_context(
            user_id=user_id,
            username=username,
            email=email
        )


def label_transaction(**labels):
    """
    Add labels to the current transaction.

    Args:
        **labels: Key-value pairs to add as labels
    """
    client = elasticapm.get_client()
    if client:
        for key, value in labels.items():
            elasticapm.label(**{key: value})


def capture_message(message: str, level: str = "info", custom: Optional[Dict] = None):
    """
    Capture a message to APM.

    Args:
        message: Message to capture
        level: Log level (debug, info, warning, error)
        custom: Custom data to attach
    """
    client = elasticapm.get_client()
    if client:
        client.capture_message(message, level=level, custom=custom)


def capture_exception(exc: Exception, custom: Optional[Dict] = None, handled: bool = True):
    """
    Capture an exception to APM.

    Args:
        exc: Exception to capture
        custom: Custom data to attach
        handled: Whether the exception was handled
    """
    client = elasticapm.get_client()
    if client:
        client.capture_exception(exc_info=(type(exc), exc, exc.__traceback__), custom=custom, handled=handled)


def get_trace_id() -> Optional[str]:
    """
    Get the current trace ID.

    Returns:
        Current trace ID or None if not available
    """
    client = elasticapm.get_client()
    if client:
        transaction = client.get_transaction()
        if transaction:
            return transaction.trace_parent.trace_id
    return None


def get_transaction_id() -> Optional[str]:
    """
    Get the current transaction ID.

    Returns:
        Current transaction ID or None if not available
    """
    client = elasticapm.get_client()
    if client:
        transaction = client.get_transaction()
        if transaction:
            return transaction.id
    return None


class APMMetrics:
    """Simple in-memory metrics tracker for demonstration."""

    def __init__(self):
        self.total_requests = 0
        self.total_response_time_ms = 0.0
        self.error_count = 0

    def record_request(self, response_time_ms: float, is_error: bool = False):
        """Record a request metric."""
        self.total_requests += 1
        self.total_response_time_ms += response_time_ms
        if is_error:
            self.error_count += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        avg_response_time = (
            self.total_response_time_ms / self.total_requests
            if self.total_requests > 0
            else 0.0
        )
        return {
            "total_requests": self.total_requests,
            "avg_response_time_ms": round(avg_response_time, 2),
            "error_count": self.error_count
        }


# Global metrics instance
_metrics = APMMetrics()


def get_metrics() -> APMMetrics:
    """Get the global metrics instance."""
    return _metrics
