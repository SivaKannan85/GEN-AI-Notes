"""
Session manager for handling conversation memory.
"""
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import ChatMessageHistory

from app.config import get_settings
from app.models import SessionInfo

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages chat sessions and their memory."""

    def __init__(self):
        """Initialize session manager."""
        self.sessions: Dict[str, dict] = {}
        self.settings = get_settings()

    def get_or_create_session(self, session_id: str) -> ConversationBufferMemory:
        """
        Get existing session memory or create a new one.

        Args:
            session_id: Unique session identifier

        Returns:
            ConversationBufferMemory instance for the session
        """
        self._cleanup_old_sessions()

        if session_id not in self.sessions:
            logger.info(f"Creating new session: {session_id}")
            memory = ConversationBufferMemory(
                memory_key=self.settings.memory_key,
                return_messages=True,
                chat_memory=ChatMessageHistory()
            )
            self.sessions[session_id] = {
                "memory": memory,
                "created_at": datetime.utcnow(),
                "last_activity": datetime.utcnow(),
                "message_count": 0
            }
        else:
            logger.info(f"Using existing session: {session_id}")
            self.sessions[session_id]["last_activity"] = datetime.utcnow()

        return self.sessions[session_id]["memory"]

    def update_session_activity(self, session_id: str):
        """Update the last activity timestamp for a session."""
        if session_id in self.sessions:
            self.sessions[session_id]["last_activity"] = datetime.utcnow()
            self.sessions[session_id]["message_count"] += 1

    def clear_session(self, session_id: str) -> bool:
        """
        Clear a specific session.

        Args:
            session_id: Session identifier to clear

        Returns:
            True if session was cleared, False if not found
        """
        if session_id in self.sessions:
            logger.info(f"Clearing session: {session_id}")
            del self.sessions[session_id]
            return True
        return False

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """
        Get information about a specific session.

        Args:
            session_id: Session identifier

        Returns:
            SessionInfo if session exists, None otherwise
        """
        if session_id not in self.sessions:
            return None

        session = self.sessions[session_id]
        return SessionInfo(
            session_id=session_id,
            message_count=session["message_count"],
            created_at=session["created_at"],
            last_activity=session["last_activity"]
        )

    def get_active_session_count(self) -> int:
        """Get the count of active sessions."""
        return len(self.sessions)

    def _cleanup_old_sessions(self):
        """Clean up sessions that have exceeded the timeout."""
        if len(self.sessions) >= self.settings.max_sessions:
            current_time = datetime.utcnow()
            timeout_delta = timedelta(minutes=self.settings.session_timeout_minutes)

            expired_sessions = [
                session_id
                for session_id, session_data in self.sessions.items()
                if current_time - session_data["last_activity"] > timeout_delta
            ]

            for session_id in expired_sessions:
                logger.info(f"Removing expired session: {session_id}")
                del self.sessions[session_id]

    def clear_all_sessions(self):
        """Clear all sessions (useful for testing)."""
        logger.info("Clearing all sessions")
        self.sessions.clear()


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
