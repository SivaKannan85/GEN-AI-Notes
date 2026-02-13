"""Tests for POC 7 Conversational RAG API."""
from fastapi.testclient import TestClient

from app.main import app, memory_manager, vectorstore_manager


client = TestClient(app)


def setup_function():
    memory_manager.clear()
    vectorstore_manager.clear()


def _index_seed_documents():
    return client.post(
        "/documents/index",
        json={
            "documents": [
                {
                    "content": "Python uses indentation to define code blocks and emphasizes readability.",
                    "source": "python-guide.md",
                },
                {
                    "content": "FastAPI is a modern web framework for building APIs with Python.",
                    "source": "fastapi-notes.md",
                },
            ]
        },
    )


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"


def test_session_lifecycle():
    create_response = client.post("/sessions")
    assert create_response.status_code == 200
    session_id = create_response.json()["session_id"]

    get_response = client.get(f"/sessions/{session_id}")
    assert get_response.status_code == 200
    assert get_response.json()["exists"] is True

    delete_response = client.delete(f"/sessions/{session_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["exists"] is False


def test_chat_requires_index():
    session_id = client.post("/sessions").json()["session_id"]
    response = client.post("/chat", json={"session_id": session_id, "message": "What is FastAPI?"})
    assert response.status_code == 400


def test_index_and_chat_with_citations_and_memory():
    index_response = _index_seed_documents()
    assert index_response.status_code == 200
    assert index_response.json()["chunks_indexed"] >= 2

    session_id = client.post("/sessions").json()["session_id"]

    first_chat = client.post(
        "/chat",
        json={"session_id": session_id, "message": "How does Python structure blocks?", "top_k": 2},
    )
    assert first_chat.status_code == 200
    first_body = first_chat.json()
    assert len(first_body["citations"]) > 0
    assert "grounded answer" in first_body["answer"].lower() or "don't have enough context" in first_body["answer"].lower()

    follow_up = client.post(
        "/chat",
        json={"session_id": session_id, "message": "And which API framework was mentioned?", "top_k": 2},
    )
    assert follow_up.status_code == 200
    follow_body = follow_up.json()
    assert follow_body["used_history_turns"] >= 1


def test_session_isolation():
    _index_seed_documents()
    s1 = client.post("/sessions").json()["session_id"]
    s2 = client.post("/sessions").json()["session_id"]

    client.post("/chat", json={"session_id": s1, "message": "Tell me about Python"})

    s1_info = client.get(f"/sessions/{s1}").json()
    s2_info = client.get(f"/sessions/{s2}").json()

    assert s1_info["message_count"] == 2
    assert s2_info["message_count"] == 0
