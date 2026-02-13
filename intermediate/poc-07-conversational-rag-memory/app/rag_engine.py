"""Simple conversational RAG engine with in-memory retrieval and session memory."""
from __future__ import annotations

from collections import defaultdict


class ConversationalRAGEngine:
    """Minimal conversational RAG engine for demo purposes."""

    def __init__(self) -> None:
        self._documents: list[str] = []
        self._sessions: dict[str, list[dict[str, str]]] = defaultdict(list)

    def ingest(self, documents: list[str]) -> int:
        cleaned = [doc.strip() for doc in documents if doc and doc.strip()]
        self._documents.extend(cleaned)
        return len(self._documents)

    def clear(self) -> None:
        self._documents.clear()
        self._sessions.clear()

    def indexed_documents(self) -> int:
        return len(self._documents)

    def ask(self, session_id: str, question: str, top_k: int = 3) -> dict:
        if not self._documents:
            raise ValueError("No documents indexed. Add documents before asking questions.")

        context = self._retrieve(question, top_k)
        history = self._sessions[session_id]

        prior_summary = ""
        if history:
            last = history[-1]
            prior_summary = f" Previous turn was about: {last['question']}"

        answer = (
            f"Based on indexed knowledge:{prior_summary} "
            f"{context[0] if context else 'No direct match found.'}"
        )

        history.append({"question": question, "answer": answer})

        return {
            "session_id": session_id,
            "question": question,
            "answer": answer,
            "context_used": context,
            "chat_history_size": len(history),
        }

    def _retrieve(self, question: str, top_k: int) -> list[str]:
        q_terms = set(question.lower().split())
        scored: list[tuple[int, str]] = []
        for doc in self._documents:
            terms = set(doc.lower().split())
            scored.append((len(q_terms.intersection(terms)), doc))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [doc for score, doc in scored[:top_k] if score > 0]


_engine: ConversationalRAGEngine | None = None


def get_engine() -> ConversationalRAGEngine:
    global _engine
    if _engine is None:
        _engine = ConversationalRAGEngine()
    return _engine
