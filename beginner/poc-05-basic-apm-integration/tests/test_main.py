"""
Unit tests for the APM-integrated FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os

# Disable APM for tests
os.environ["ELASTIC_APM_ENABLED"] = "false"

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "apm_enabled" in data
    assert "timestamp" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_get_metrics(client):
    """Test getting application metrics."""
    # Make a few requests first
    client.get("/health")
    client.get("/health")

    # Get metrics
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "avg_response_time_ms" in data
    assert "error_count" in data
    assert data["total_requests"] >= 2


def test_create_task_success(client):
    """Test creating a task successfully."""
    request_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "priority": "high"
    }
    response = client.post("/tasks", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["title"] == "Test Task"
    assert data["description"] == "This is a test task"
    assert data["priority"] == "high"
    assert "created_at" in data
    assert "processing_time_ms" in data
    assert data["processing_time_ms"] > 0


def test_create_task_minimal(client):
    """Test creating a task with minimal data."""
    request_data = {
        "title": "Minimal Task"
    }
    response = client.post("/tasks", json=request_data)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Minimal Task"
    assert data["priority"] == "medium"  # Default priority


def test_create_task_invalid(client):
    """Test creating a task with invalid data."""
    request_data = {
        "title": ""  # Empty title should fail validation
    }
    response = client.post("/tasks", json=request_data)
    assert response.status_code == 422


def test_process_data_success(client):
    """Test data processing endpoint."""
    request_data = {
        "items": ["item1", "item2", "item3"],
        "delay_ms": 10  # Small delay for faster tests
    }
    response = client.post("/process", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["processed_count"] == 3
    assert data["total_time_ms"] > 0
    assert data["items"] == ["ITEM1", "ITEM2", "ITEM3"]


def test_process_data_with_default_delay(client):
    """Test data processing with default delay."""
    request_data = {
        "items": ["test"]
    }
    response = client.post("/process", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["processed_count"] == 1
    assert data["items"] == ["TEST"]


def test_process_data_invalid(client):
    """Test data processing with invalid input."""
    request_data = {
        "items": []  # Empty list should fail
    }
    response = client.post("/process", json=request_data)
    assert response.status_code == 422


def test_trigger_error(client):
    """Test error triggering endpoint."""
    response = client.get("/error/test")
    assert response.status_code == 500
    data = response.json()
    assert "error" in data or "detail" in data


def test_slow_endpoint(client):
    """Test slow endpoint."""
    response = client.get("/slow")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_metrics_middleware(client):
    """Test that metrics middleware tracks requests."""
    # Get initial metrics
    metrics_before = client.get("/metrics").json()
    initial_count = metrics_before["total_requests"]

    # Make a request
    client.get("/health")

    # Check metrics updated
    metrics_after = client.get("/metrics").json()
    assert metrics_after["total_requests"] > initial_count


def test_metrics_error_tracking(client):
    """Test that metrics track errors."""
    # Get initial error count
    metrics_before = client.get("/metrics").json()
    initial_errors = metrics_before["error_count"]

    # Trigger an error
    client.get("/error/test")

    # Check error count increased
    metrics_after = client.get("/metrics").json()
    assert metrics_after["error_count"] > initial_errors


@patch('app.apm_utils.elasticapm.get_client')
def test_apm_utils_with_client(mock_get_client):
    """Test APM utilities when client is available."""
    from app.apm_utils import get_trace_id, get_transaction_id

    # Setup mock
    mock_client = MagicMock()
    mock_transaction = MagicMock()
    mock_transaction.trace_parent.trace_id = "test-trace-id"
    mock_transaction.id = "test-transaction-id"
    mock_client.get_transaction.return_value = mock_transaction
    mock_get_client.return_value = mock_client

    # Test trace ID
    trace_id = get_trace_id()
    assert trace_id == "test-trace-id"

    # Test transaction ID
    transaction_id = get_transaction_id()
    assert transaction_id == "test-transaction-id"


@patch('app.apm_utils.elasticapm.get_client')
def test_apm_utils_without_client(mock_get_client):
    """Test APM utilities when client is not available."""
    from app.apm_utils import get_trace_id, get_transaction_id

    # Setup mock to return None
    mock_get_client.return_value = None

    # Test trace ID
    trace_id = get_trace_id()
    assert trace_id is None

    # Test transaction ID
    transaction_id = get_transaction_id()
    assert transaction_id is None


def test_concurrent_requests(client):
    """Test handling concurrent requests."""
    import concurrent.futures

    def make_request():
        return client.get("/health")

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(make_request) for _ in range(10)]
        results = [f.result() for f in futures]

    # All requests should succeed
    assert all(r.status_code == 200 for r in results)

    # Metrics should track all requests
    metrics = client.get("/metrics").json()
    assert metrics["total_requests"] >= 10
