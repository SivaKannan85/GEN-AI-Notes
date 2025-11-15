"""
Unit tests for the LangChain chatbot application.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock

from app.main import app
from app.session_manager import get_session_manager


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_sessions():
    """Clear all sessions before and after each test."""
    session_manager = get_session_manager()
    session_manager.clear_all_sessions()
    yield
    session_manager.clear_all_sessions()


@pytest.fixture
def mock_chatbot_response():
    """Create a mock chatbot response."""
    return {
        "response": "Hello! I'm a helpful AI assistant. How can I help you today?",
        "conversation_history": [
            {
                "role": "user",
                "content": "Hello",
                "timestamp": None
            },
            {
                "role": "assistant",
                "content": "Hello! I'm a helpful AI assistant. How can I help you today?",
                "timestamp": None
            }
        ],
        "tokens_used": 25
    }


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "active_sessions" in data
    assert data["active_sessions"] == 0


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "active_sessions" in data


@patch('app.chatbot.LangChainChatbot.chat')
def test_chat_success(mock_chat, client, mock_chatbot_response):
    """Test successful chat interaction."""
    # Setup mock
    mock_chat.return_value = mock_chatbot_response

    # Make request
    request_data = {
        "session_id": "test-session-1",
        "message": "Hello",
        "temperature": 0.7
    }
    response = client.post("/chat", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-1"
    assert data["message"] == "Hello! I'm a helpful AI assistant. How can I help you today?"
    assert len(data["conversation_history"]) == 2
    assert data["tokens_used"] == 25


@patch('app.chatbot.LangChainChatbot.chat')
def test_chat_multiple_messages(mock_chat, client, mock_chatbot_response):
    """Test multiple chat messages in same session."""
    # Setup mock
    mock_chat.return_value = mock_chatbot_response

    session_id = "test-session-multi"

    # First message
    response1 = client.post("/chat", json={
        "session_id": session_id,
        "message": "Hello"
    })
    assert response1.status_code == 200

    # Second message
    response2 = client.post("/chat", json={
        "session_id": session_id,
        "message": "How are you?"
    })
    assert response2.status_code == 200
    assert response2.json()["session_id"] == session_id


def test_chat_invalid_request(client):
    """Test chat with invalid request."""
    request_data = {
        "session_id": "",  # Empty session_id should fail
        "message": "Hello"
    }
    response = client.post("/chat", json=request_data)
    assert response.status_code == 422  # Validation error


@patch('app.chatbot.LangChainChatbot.chat')
def test_get_session_info(mock_chat, client, mock_chatbot_response):
    """Test getting session information."""
    # Setup mock
    mock_chat.return_value = mock_chatbot_response

    session_id = "test-session-info"

    # Create a session by sending a message
    client.post("/chat", json={
        "session_id": session_id,
        "message": "Hello"
    })

    # Get session info
    response = client.get(f"/session/{session_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert data["message_count"] >= 1
    assert "created_at" in data
    assert "last_activity" in data


def test_get_session_not_found(client):
    """Test getting info for non-existent session."""
    response = client.get("/session/nonexistent-session")
    assert response.status_code == 404


@patch('app.chatbot.LangChainChatbot.chat')
def test_clear_session(mock_chat, client, mock_chatbot_response):
    """Test clearing a session."""
    # Setup mock
    mock_chat.return_value = mock_chatbot_response

    session_id = "test-session-clear"

    # Create a session
    client.post("/chat", json={
        "session_id": session_id,
        "message": "Hello"
    })

    # Verify session exists
    response = client.get(f"/session/{session_id}")
    assert response.status_code == 200

    # Clear the session
    response = client.post("/session/clear", json={
        "session_id": session_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "cleared successfully" in data["message"].lower()

    # Verify session is gone
    response = client.get(f"/session/{session_id}")
    assert response.status_code == 404


def test_clear_nonexistent_session(client):
    """Test clearing a non-existent session."""
    response = client.post("/session/clear", json={
        "session_id": "nonexistent-session"
    })
    assert response.status_code == 404


@patch('app.chatbot.LangChainChatbot.chat')
def test_temperature_parameter(mock_chat, client, mock_chatbot_response):
    """Test that temperature parameter is passed correctly."""
    # Setup mock
    mock_chat.return_value = mock_chatbot_response

    # Make request with custom temperature
    request_data = {
        "session_id": "test-temp",
        "message": "Hello",
        "temperature": 1.5
    }
    response = client.post("/chat", json=request_data)
    assert response.status_code == 200

    # Verify temperature was passed to chatbot
    mock_chat.assert_called_once()
    call_args = mock_chat.call_args
    assert call_args[1]["temperature"] == 1.5
