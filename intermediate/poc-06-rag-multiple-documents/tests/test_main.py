"""
Tests for POC 6: RAG System with Multiple Document Types
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO

# We'll mock the entire app to avoid needing real OpenAI credentials
@pytest.fixture
def mock_vectorstore_manager():
    """Mock vectorstore manager"""
    mock = Mock()
    mock.add_documents = Mock(return_value={
        "filename": "test.txt",
        "file_type": "txt",
        "upload_timestamp": "2024-01-15T10:30:00",
        "file_size_bytes": 1024,
        "page_count": None,
        "category": None,
        "tags": [],
        "custom_metadata": {}
    })
    mock.similarity_search_with_filter = Mock(return_value=[
        (Mock(page_content="Test content", metadata={"source": "test.txt", "file_type": "txt"}), 0.85)
    ])
    mock.list_documents = Mock(return_value=[
        {
            "filename": "test.txt",
            "file_type": "txt",
            "upload_timestamp": "2024-01-15T10:30:00",
            "file_size_bytes": 1024,
        }
    ])
    mock.get_document_stats = Mock(return_value={
        "total_documents": 1,
        "documents_by_type": {"txt": 1}
    })
    return mock


@pytest.fixture
def mock_qa_chain():
    """Mock QA chain"""
    mock = Mock()
    mock.ask = Mock(return_value={
        "question": "What is the revenue?",
        "answer": "The revenue is $12.5 million.",
        "sources": [
            {
                "source": "test.txt",
                "content": "Total revenue: $12.5 million",
                "metadata": {"source": "test.txt"},
                "relevance_score": 0.85
            }
        ],
        "total_sources": 1
    })
    return mock


@pytest.fixture
def client(mock_vectorstore_manager, mock_qa_chain):
    """Test client with mocked dependencies"""
    with patch('app.main.vectorstore_manager', mock_vectorstore_manager), \
         patch('app.main.qa_chain', mock_qa_chain):
        from app.main import app
        with TestClient(app) as test_client:
            yield test_client


def test_root_endpoint(client):
    """Test root endpoint returns health status"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "RAG System" in data["message"]


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch('app.main.DocumentLoaderFactory')
@patch('app.main.DocumentChunker')
def test_upload_txt_document(mock_chunker_class, mock_loader_class, client, mock_vectorstore_manager):
    """Test uploading a TXT document"""
    # Setup mocks
    mock_loader_class.load_document = Mock(return_value=[
        Mock(page_content="Test content", metadata={"source": "test.txt"})
    ])
    mock_chunker = Mock()
    mock_chunker.chunk_documents = Mock(return_value=[
        Mock(page_content="Test content", metadata={"source": "test.txt"})
    ])
    mock_chunker_class.return_value = mock_chunker

    # Create a test file
    file_content = b"This is a test document."
    file = ("test.txt", BytesIO(file_content), "text/plain")

    # Upload the file
    response = client.post(
        "/upload",
        files={"file": file},
        data={"chunking_strategy": "recursive"}
    )

    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["chunks_created"] >= 0


@patch('app.main.DocumentLoaderFactory')
@patch('app.main.DocumentChunker')
def test_upload_markdown_document(mock_chunker_class, mock_loader_class, client):
    """Test uploading a Markdown document"""
    # Setup mocks
    mock_loader_class.load_document = Mock(return_value=[
        Mock(page_content="# Test\nContent", metadata={"source": "test.md"})
    ])
    mock_chunker = Mock()
    mock_chunker.chunk_documents = Mock(return_value=[
        Mock(page_content="# Test\nContent", metadata={"source": "test.md"})
    ])
    mock_chunker_class.return_value = mock_chunker

    # Create a test file
    file_content = b"# Test\nThis is a test markdown document."
    file = ("test.md", BytesIO(file_content), "text/markdown")

    # Upload the file
    response = client.post(
        "/upload",
        files={"file": file},
        data={"chunking_strategy": "recursive"}
    )

    assert response.status_code == 200


def test_upload_unsupported_format(client):
    """Test uploading an unsupported file format"""
    file_content = b"Test content"
    file = ("test.xyz", BytesIO(file_content), "application/octet-stream")

    response = client.post(
        "/upload",
        files={"file": file}
    )

    assert response.status_code == 400
    assert "Unsupported file type" in response.json()["detail"]


def test_ask_question(client, mock_qa_chain):
    """Test asking a question"""
    request_data = {
        "question": "What is the revenue?",
        "top_k": 4,
        "filter_metadata": None
    }

    response = client.post("/ask", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is the revenue?"
    assert "answer" in data
    assert "sources" in data


def test_ask_question_with_filters(client, mock_qa_chain):
    """Test asking a question with metadata filters"""
    request_data = {
        "question": "What is the revenue?",
        "top_k": 4,
        "filter_metadata": {"file_type": "txt"}
    }

    response = client.post("/ask", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "answer" in data


def test_list_documents(client, mock_vectorstore_manager):
    """Test listing documents"""
    response = client.get("/documents")

    assert response.status_code == 200
    data = response.json()
    assert "total_documents" in data
    assert "documents" in data
    assert "stats" in data


def test_delete_document_not_implemented(client):
    """Test that document deletion returns not implemented"""
    response = client.delete("/documents/test-doc-id")

    assert response.status_code == 501
    assert "not yet implemented" in response.json()["detail"].lower()


@pytest.mark.parametrize("question,top_k", [
    ("What is the revenue?", 4),
    ("What are the challenges?", 10),
    ("Summary of Q4", 2),
])
def test_ask_various_questions(client, mock_qa_chain, question, top_k):
    """Test asking various questions with different top_k values"""
    request_data = {
        "question": question,
        "top_k": top_k,
    }

    response = client.post("/ask", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["question"] == question


def test_ask_question_empty_question(client):
    """Test asking an empty question"""
    request_data = {
        "question": "",
        "top_k": 4,
    }

    response = client.post("/ask", json=request_data)

    assert response.status_code == 422  # Validation error


def test_ask_question_invalid_top_k(client):
    """Test asking with invalid top_k"""
    request_data = {
        "question": "Test question",
        "top_k": 100,  # Exceeds maximum
    }

    response = client.post("/ask", json=request_data)

    assert response.status_code == 422  # Validation error
