"""In-memory session manager for conversational context."""
from datetime import datetime, timezone
from uuid import uuid4


class MemoryManager:
    """Manage per-session conversational history."""

    def __init__(self, max_history_turns: int = 5):
        self.max_history_turns = max_history_turns
        self._sessions: dict[str, dict] = {}

    def create_session(self) -> tuple[str, datetime]:
        session_id = str(uuid4())
        created_at = datetime.now(timezone.utc)
        self._sessions[session_id] = {"created_at": created_at, "messages": []}
        return session_id, created_at

    def ensure_session(self, session_id: str) -> None:
        if session_id not in self._sessions:
            self._sessions[session_id] = {"created_at": datetime.now(timezone.utc), "messages": []}

    def session_exists(self, session_id: str) -> bool:
        return session_id in self._sessions

    def add_turn(self, session_id: str, user_message: str, assistant_message: str) -> None:
        self.ensure_session(session_id)
        session = self._sessions[session_id]
        session["messages"].append({"role": "user", "content": user_message})
        session["messages"].append({"role": "assistant", "content": assistant_message})

        max_messages = self.max_history_turns * 2
        if len(session["messages"]) > max_messages:
            session["messages"] = session["messages"][-max_messages:]

    def get_history(self, session_id: str) -> list[dict[str, str]]:
        if session_id not in self._sessions:
            return []
        return list(self._sessions[session_id]["messages"])

    def get_message_count(self, session_id: str) -> int:
        if session_id not in self._sessions:
            return 0
        return len(self._sessions[session_id]["messages"])

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def session_count(self) -> int:
        return len(self._sessions)

    def clear(self) -> None:
        self._sessions.clear()
