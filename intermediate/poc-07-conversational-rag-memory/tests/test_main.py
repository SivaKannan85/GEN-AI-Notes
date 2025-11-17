"""
Tests for POC 7: Conversational RAG with Memory
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Mock the entire app to avoid needing real OpenAI credentials
@pytest.fixture
def mock_session_manager():
    """Mock session manager"""
    mock = Mock()
    mock_session = Mock()
    mock_session.session_id = "test-session-123"
    mock_session.session_name = "Test Session"
    mock_session.created_at = datetime.utcnow()
    mock_session.last_activity = datetime.utcnow()
    mock_session.messages = []
    mock_session.add_message = Mock()
    mock_session.get_conversation_history = Mock(return_value={
        "session_id": "test-session-123",
        "messages": [],
        "total_messages": 0
    })
    mock_session.get_session_info = Mock(return_value={
        "session_id": "test-session-123",
        "session_name": "Test Session",
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "message_count": 0,
        "metadata": {}
    })

    mock.create_session = Mock(return_value=mock_session)
    mock.get_session = Mock(return_value=mock_session)
    mock.delete_session = Mock(return_value=True)
    mock.list_sessions = Mock(return_value=[mock_session.get_session_info()])
    mock.get_active_session_count = Mock(return_value=1)

    return mock


@pytest.fixture
def mock_rag_chain():
    """Mock RAG chain"""
    mock = Mock()
    mock.ask = Mock(return_value=(
        "This is a test answer based on the conversation history.",
        [],  # sources
        False  # retrieval_used
    ))
    return mock


@pytest.fixture
def client(mock_session_manager, mock_rag_chain):
    """Test client with mocked dependencies"""
    with patch('app.main.session_manager', mock_session_manager), \
         patch('app.main.rag_chain', mock_rag_chain):
        from app.main import app
        with TestClient(app) as test_client:
            yield test_client


def test_root_endpoint(client):
    """Test root endpoint returns health status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Conversational RAG" in data["message"]
    assert "active_sessions" in data


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["active_sessions"] >= 0


def test_create_session(client, mock_session_manager):
    """Test creating a new session"""
    request_data = {
        "session_name": "My Conversation",
        "metadata": {"user_id": "user123"}
    }

    response = client.post("/sessions", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data
    assert "created_at" in data
    assert "message" in data


def test_create_session_without_name(client):
    """Test creating a session without a name"""
    response = client.post("/sessions", json={})

    assert response.status_code == 200
    data = response.json()
    assert "session_id" in data


def test_list_sessions(client, mock_session_manager):
    """Test listing all sessions"""
    response = client.get("/sessions")

    assert response.status_code == 200
    data = response.json()
    assert "sessions" in data
    assert "total_sessions" in data
    assert data["total_sessions"] >= 0


def test_get_session_history(client, mock_session_manager):
    """Test getting session history"""
    session_id = "test-session-123"

    response = client.get(f"/sessions/{session_id}/history")

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == session_id
    assert "messages" in data
    assert "total_messages" in data


def test_get_session_history_not_found(client, mock_session_manager):
    """Test getting history for non-existent session"""
    mock_session_manager.get_session.return_value = None

    response = client.get("/sessions/nonexistent/history")

    assert response.status_code == 404


def test_delete_session(client, mock_session_manager):
    """Test deleting a session"""
    session_id = "test-session-123"

    response = client.delete(f"/sessions/{session_id}")

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_delete_session_not_found(client, mock_session_manager):
    """Test deleting non-existent session"""
    mock_session_manager.delete_session.return_value = False

    response = client.delete("/sessions/nonexistent")

    assert response.status_code == 404


def test_chat(client, mock_session_manager, mock_rag_chain):
    """Test chatting in a session"""
    request_data = {
        "session_id": "test-session-123",
        "message": "What was the Q4 revenue?",
        "use_retrieval": False,
        "top_k": 4
    }

    response = client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "test-session-123"
    assert "message" in data
    assert "sources" in data
    assert "conversation_context_used" in data
    assert "retrieval_used" in data


def test_chat_with_retrieval(client, mock_session_manager, mock_rag_chain):
    """Test chatting with retrieval enabled"""
    mock_rag_chain.ask.return_value = (
        "The revenue was $12.5 million.",
        [{"source": "report.txt", "content": "...", "metadata": {}, "relevance_score": 0.9}],
        True
    )

    request_data = {
        "session_id": "test-session-123",
        "message": "What was the revenue?",
        "use_retrieval": True,
        "top_k": 4
    }

    response = client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["retrieval_used"] == True


def test_chat_session_not_found(client, mock_session_manager):
    """Test chatting with non-existent session"""
    mock_session_manager.get_session.return_value = None

    request_data = {
        "session_id": "nonexistent",
        "message": "Test message"
    }

    response = client.post("/chat", json=request_data)

    assert response.status_code == 404


@pytest.mark.parametrize("message", [
    "Hello!",
    "What is the revenue?",
    "Can you explain the Q4 results?",
    "Tell me about the company growth."
])
def test_chat_various_messages(client, mock_session_manager, message):
    """Test chatting with various messages"""
    request_data = {
        "session_id": "test-session-123",
        "message": message,
        "use_retrieval": False
    }

    response = client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "message" in data


def test_chat_empty_message(client):
    """Test chatting with empty message"""
    request_data = {
        "session_id": "test-session-123",
        "message": "",
        "use_retrieval": False
    }

    response = client.post("/chat", json=request_data)

    assert response.status_code == 422  # Validation error


def test_chat_invalid_session_id(client):
    """Test chatting without session_id"""
    request_data = {
        "message": "Test message"
    }

    response = client.post("/chat", json=request_data)

    assert response.status_code == 422  # Validation error
