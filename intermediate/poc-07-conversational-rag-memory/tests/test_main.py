from fastapi.testclient import TestClient

from app.main import app
from app.rag_engine import get_engine


client = TestClient(app)


def setup_function() -> None:
    get_engine().clear()


def test_health_endpoint() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_ingest_and_chat_flow_with_memory() -> None:
    ingest_response = client.post(
        "/documents/ingest",
        json={"documents": ["FastAPI is a modern web framework", "FAISS powers similarity search"]},
    )
    assert ingest_response.status_code == 201
    assert ingest_response.json()["indexed_documents"] == 2

    first = client.post(
        "/chat/ask",
        json={"session_id": "s1", "question": "What is FastAPI?", "top_k": 1},
    )
    assert first.status_code == 200
    assert first.json()["chat_history_size"] == 1

    second = client.post(
        "/chat/ask",
        json={"session_id": "s1", "question": "And what about search?", "top_k": 1},
    )
    assert second.status_code == 200
    assert second.json()["chat_history_size"] == 2
    assert "Previous turn was about" in second.json()["answer"]


def test_ask_requires_documents() -> None:
    response = client.post(
        "/chat/ask",
        json={"session_id": "s1", "question": "hello", "top_k": 1},
    )
    assert response.status_code == 400
