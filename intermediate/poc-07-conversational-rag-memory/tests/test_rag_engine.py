from app.rag_engine import ConversationalRAGEngine


def test_retrieve_returns_empty_when_all_scores_are_zero() -> None:
    engine = ConversationalRAGEngine()
    engine.ingest(["FastAPI framework", "Vector database search"])

    assert engine._retrieve("quantum mechanics", top_k=2) == []


def test_retrieve_returns_empty_for_non_positive_top_k() -> None:
    engine = ConversationalRAGEngine()
    engine.ingest(["FastAPI framework"])

    assert engine._retrieve("FastAPI", top_k=0) == []


def test_ask_uses_no_match_message_when_context_is_empty() -> None:
    engine = ConversationalRAGEngine()
    engine.ingest(["FastAPI framework", "Vector database search"])

    response = engine.ask("session-1", "quantum mechanics")

    assert response["context_used"] == []
    assert "No direct match found." in response["answer"]
