import os

os.environ.setdefault("OPENAI_API_KEY", "test-key")

"""Unit tests for POC 6 multi-document RAG service."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from langchain.schema import Document

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture(autouse=True)
def clear_vectorstore():
    from app.vectorstore_manager import get_vectorstore_manager

    manager = get_vectorstore_manager()
    manager.clear()
    yield
    manager.clear()


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "vectorstore_initialized" in body


@patch("app.document_processor.DocumentProcessor.process_uploads")
@patch("app.vectorstore_manager.VectorStoreManager.add_documents")
def test_upload_documents_success(mock_add_docs, mock_process_uploads, client):
    mock_process_uploads.return_value = [Document(page_content="chunk", metadata={})]
    mock_add_docs.return_value = 1

    payload = {
        "documents": [
            {
                "filename": "notes.md",
                "document_type": "md",
                "content": "# Title\nHello world",
                "metadata": {"source": "notes"},
            }
        ]
    }

    response = client.post("/documents/upload", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["documents_received"] == 1
    assert body["chunks_added"] == 1


def test_upload_documents_validation(client):
    response = client.post(
        "/documents/upload",
        json={"documents": [{"filename": "a.pdf", "document_type": "pdf"}]},
    )
    assert response.status_code == 422


@patch("app.qa_chain.QAChain.answer_question")
def test_ask_question_success(mock_answer_question, client):
    mock_answer_question.return_value = {
        "answer": "Python is a programming language.",
        "source_documents": [
            Document(page_content="Python is a language", metadata={"source": "guide.txt"})
        ],
    }

    response = client.post(
        "/ask",
        json={
            "question": "What is Python?",
            "top_k": 3,
            "filters": {"document_type": "txt", "source": "guide.txt"},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["question"] == "What is Python?"
    assert body["answer"]
    assert len(body["source_documents"]) == 1


def test_ask_question_validation(client):
    response = client.post("/ask", json={"question": "", "top_k": 2})
    assert response.status_code == 422


@patch("app.vectorstore_manager.VectorStoreManager.is_initialized")
def test_ask_question_no_documents(mock_initialized, client):
    mock_initialized.return_value = False

    response = client.post("/ask", json={"question": "Any docs?"})
    assert response.status_code == 400


def test_vectorstore_info(client):
    response = client.get("/vectorstore/info")
    assert response.status_code == 200
    body = response.json()
    assert "document_count" in body
    assert "is_initialized" in body


def test_clear_vectorstore(client):
    response = client.delete("/vectorstore/clear")
    assert response.status_code == 200
    assert "message" in response.json()
