"""
Unit tests for the Document QA application.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from langchain.schema import Document

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_vectorstore():
    """Clear vectorstore before and after each test."""
    from app.vectorstore_manager import get_vectorstore_manager
    vectorstore_manager = get_vectorstore_manager()
    vectorstore_manager.clear()
    yield
    vectorstore_manager.clear()


@pytest.fixture
def sample_document():
    """Sample document for testing."""
    return {
        "content": "Python is a high-level programming language. It is known for its simplicity and readability.",
        "metadata": {"source": "test.txt"}
    }


@pytest.fixture
def mock_qa_result():
    """Mock QA chain result."""
    return {
        "answer": "Python is a high-level programming language known for simplicity.",
        "source_documents": [
            Document(
                page_content="Python is a high-level programming language.",
                metadata={"source": "test.txt"}
            )
        ]
    }


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "vectorstore_initialized" in data


def test_root_endpoint(client):
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@patch('app.vectorstore_manager.VectorStoreManager.add_documents')
@patch('app.document_processor.DocumentProcessor.process_text')
def test_upload_document_success(mock_process, mock_add, client, sample_document):
    """Test successful document upload."""
    # Setup mocks
    mock_chunks = [
        Document(page_content="Python is a high-level programming language.", metadata={"source": "test.txt"}),
        Document(page_content="It is known for its simplicity and readability.", metadata={"source": "test.txt"})
    ]
    mock_process.return_value = mock_chunks
    mock_add.return_value = len(mock_chunks)

    # Make request
    response = client.post("/documents/upload", json=sample_document)

    # Assertions
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Documents uploaded successfully"
    assert data["chunks_added"] == 2


def test_upload_document_invalid_request(client):
    """Test document upload with invalid request."""
    response = client.post("/documents/upload", json={"content": ""})
    assert response.status_code == 422  # Validation error


@patch('app.qa_chain.QAChain.answer_question')
@patch('app.vectorstore_manager.VectorStoreManager.is_initialized')
def test_ask_question_success(mock_initialized, mock_answer, client, mock_qa_result):
    """Test successful question answering."""
    # Setup mocks
    mock_initialized.return_value = True
    mock_answer.return_value = mock_qa_result

    # Make request
    request_data = {
        "question": "What is Python?",
        "top_k": 3
    }
    response = client.post("/ask", json=request_data)

    # Assertions
    assert response.status_code == 200
    data = response.json()
    assert data["question"] == "What is Python?"
    assert "answer" in data
    assert len(data["source_documents"]) > 0


@patch('app.vectorstore_manager.VectorStoreManager.is_initialized')
def test_ask_question_no_documents(mock_initialized, client):
    """Test asking question without uploaded documents."""
    # Setup mock
    mock_initialized.return_value = False

    # Make request
    request_data = {
        "question": "What is Python?"
    }
    response = client.post("/ask", json=request_data)

    # Should return 400
    assert response.status_code == 400


def test_ask_question_invalid_request(client):
    """Test asking question with invalid request."""
    response = client.post("/ask", json={"question": ""})
    assert response.status_code == 422  # Validation error


def test_get_vectorstore_info(client):
    """Test getting vectorstore information."""
    response = client.get("/vectorstore/info")
    assert response.status_code == 200
    data = response.json()
    assert "document_count" in data
    assert "is_initialized" in data
    assert isinstance(data["document_count"], int)
    assert isinstance(data["is_initialized"], bool)


def test_clear_vectorstore(client):
    """Test clearing vectorstore."""
    response = client.delete("/vectorstore/clear")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@patch('app.vectorstore_manager.VectorStoreManager.add_documents')
@patch('app.document_processor.DocumentProcessor.process_text')
@patch('app.qa_chain.QAChain.answer_question')
@patch('app.vectorstore_manager.VectorStoreManager.is_initialized')
def test_full_workflow(mock_initialized, mock_answer, mock_process, mock_add, client, sample_document, mock_qa_result):
    """Test full workflow: upload document and ask question."""
    # Setup mocks
    mock_chunks = [Document(page_content="Python is a high-level programming language.", metadata={})]
    mock_process.return_value = mock_chunks
    mock_add.return_value = 1
    mock_initialized.return_value = True
    mock_answer.return_value = mock_qa_result

    # Upload document
    upload_response = client.post("/documents/upload", json=sample_document)
    assert upload_response.status_code == 201

    # Ask question
    question_response = client.post("/ask", json={"question": "What is Python?"})
    assert question_response.status_code == 200
    assert "answer" in question_response.json()


def test_top_k_parameter(client):
    """Test that top_k parameter is validated."""
    # Valid top_k
    response = client.post("/ask", json={"question": "What is Python?", "top_k": 5})
    # Will fail with no documents, but should pass validation
    assert response.status_code in [200, 400]  # 400 if no docs, 200 if mocked

    # Invalid top_k (too large)
    response = client.post("/ask", json={"question": "What is Python?", "top_k": 20})
    assert response.status_code == 422  # Validation error
