"""
Unit tests for the FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from openai.types.chat import ChatCompletion, ChatCompletionMessage
from openai.types.chat.chat_completion import Choice
from openai.types.completion_usage import CompletionUsage

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def mock_openai_response():
    """Create a mock OpenAI response."""
    return ChatCompletion(
        id="test-id",
        choices=[
            Choice(
                finish_reason="stop",
                index=0,
                message=ChatCompletionMessage(
                    content="This is a test response from OpenAI.",
                    role="assistant"
                )
            )
        ],
        created=1234567890,
        model="gpt-3.5-turbo",
        object="chat.completion",
        usage=CompletionUsage(
            completion_tokens=10,
            prompt_tokens=20,
            total_tokens=30
        )
    )


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@patch('app.main.openai_client')
def test_chat_completion_success(mock_client, client, mock_openai_response):
    """Test successful chat completion."""
    # Setup mock
    mock_client.chat.completions.create.return_value = mock_openai_response

    # Make request
    request_data = {
        "message": "What is FastAPI?",
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7,
        "max_tokens": 500
    }
    response = client.post("/chat", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert "response" in data
    assert data["response"] == "This is a test response from OpenAI."
    assert data["model"] == "gpt-3.5-turbo"
    assert data["tokens_used"] == 30
    assert data["finish_reason"] == "stop"


def test_chat_completion_invalid_request(client):
    """Test chat completion with invalid request."""
    request_data = {
        "message": "",  # Empty message should fail validation
    }
    response = client.post("/chat", json=request_data)
    assert response.status_code == 422  # Validation error


@patch('app.main.openai_client')
def test_chat_completion_openai_error(mock_client, client):
    """Test chat completion with OpenAI API error."""
    from openai import APIError

    # Setup mock to raise error
    mock_client.chat.completions.create.side_effect = APIError(
        message="Test API error",
        request=Mock(),
        body={}
    )

    # Make request
    request_data = {
        "message": "What is FastAPI?"
    }
    response = client.post("/chat", json=request_data)

    # Should return 502 for API errors
    assert response.status_code == 502
