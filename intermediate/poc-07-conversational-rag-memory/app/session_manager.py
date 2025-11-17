"""
Session management for conversational RAG system.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from langchain.memory import ConversationBufferMemory
from langchain.schema import HumanMessage, AIMessage

from app.models import (
    ChatMessage,
    MessageRole,
    SessionInfo,
    ConversationHistory,
)

logger = logging.getLogger(__name__)


class Session:
    """Individual conversation session."""

    def __init__(
        self,
        session_id: str,
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        max_history: int = 20,
    ):
        """
        Initialize a session.

        Args:
            session_id: Unique session identifier
            session_name: Optional session name
            metadata: Optional session metadata
            max_history: Maximum number of messages to keep in memory
        """
        self.session_id = session_id
        self.session_name = session_name
        self.metadata = metadata or {}
        self.created_at = datetime.utcnow()
        self.last_activity = datetime.utcnow()
        self.max_history = max_history

        # LangChain conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )

        # Complete message history (for display/export)
        self.messages: List[ChatMessage] = []

        logger.info(f"Created session: {session_id}")

    def add_message(self, role: MessageRole, content: str) -> None:
        """
        Add a message to the session.

        Args:
            role: Message role (user/assistant)
            content: Message content
        """
        message = ChatMessage(
            role=role,
            content=content,
            timestamp=datetime.utcnow(),
        )
        self.messages.append(message)
        self.last_activity = datetime.utcnow()

        # Add to LangChain memory
        if role == MessageRole.USER:
            self.memory.chat_memory.add_user_message(content)
        elif role == MessageRole.ASSISTANT:
            self.memory.chat_memory.add_ai_message(content)

        # Trim history if needed
        self._trim_history()

        logger.debug(f"Added {role} message to session {self.session_id}")

    def _trim_history(self) -> None:
        """Trim message history to max_history."""
        if len(self.messages) > self.max_history:
            # Keep the latest max_history messages
            self.messages = self.messages[-self.max_history:]

            # Also trim the LangChain memory
            if len(self.memory.chat_memory.messages) > self.max_history:
                self.memory.chat_memory.messages = self.memory.chat_memory.messages[-self.max_history:]

    def get_conversation_history(self) -> ConversationHistory:
        """
        Get the conversation history.

        Returns:
            ConversationHistory object
        """
        return ConversationHistory(
            session_id=self.session_id,
            messages=self.messages,
            total_messages=len(self.messages),
        )

    def get_session_info(self) -> SessionInfo:
        """
        Get session information.

        Returns:
            SessionInfo object
        """
        return SessionInfo(
            session_id=self.session_id,
            session_name=self.session_name,
            created_at=self.created_at,
            last_activity=self.last_activity,
            message_count=len(self.messages),
            metadata=self.metadata,
        )

    def is_expired(self, timeout_minutes: int) -> bool:
        """
        Check if session is expired.

        Args:
            timeout_minutes: Timeout in minutes

        Returns:
            True if expired, False otherwise
        """
        timeout = timedelta(minutes=timeout_minutes)
        return (datetime.utcnow() - self.last_activity) > timeout


class SessionManager:
    """Manager for all conversation sessions."""

    def __init__(
        self,
        max_history: int = 20,
        session_timeout_minutes: int = 60,
    ):
        """
        Initialize the session manager.

        Args:
            max_history: Maximum messages per session
            session_timeout_minutes: Session timeout in minutes
        """
        self.sessions: Dict[str, Session] = {}
        self.max_history = max_history
        self.session_timeout_minutes = session_timeout_minutes

        logger.info("Initialized SessionManager")

    def create_session(
        self,
        session_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Session:
        """
        Create a new session.

        Args:
            session_name: Optional session name
            metadata: Optional session metadata

        Returns:
            Created Session object
        """
        session_id = f"sess-{uuid.uuid4().hex[:12]}"

        session = Session(
            session_id=session_id,
            session_name=session_name,
            metadata=metadata,
            max_history=self.max_history,
        )

        self.sessions[session_id] = session
        logger.info(f"Created new session: {session_id}")

        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        """
        Get a session by ID.

        Args:
            session_id: Session identifier

        Returns:
            Session object or None if not found
        """
        session = self.sessions.get(session_id)

        if session and session.is_expired(self.session_timeout_minutes):
            logger.info(f"Session {session_id} has expired")
            self.delete_session(session_id)
            return None

        return session

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Deleted session: {session_id}")
            return True
        return False

    def list_sessions(self) -> List[SessionInfo]:
        """
        List all active sessions.

        Returns:
            List of SessionInfo objects
        """
        # Cleanup expired sessions first
        self.cleanup_expired_sessions()

        return [session.get_session_info() for session in self.sessions.values()]

    def cleanup_expired_sessions(self) -> int:
        """
        Cleanup expired sessions.

        Returns:
            Number of sessions cleaned up
        """
        expired = [
            session_id
            for session_id, session in self.sessions.items()
            if session.is_expired(self.session_timeout_minutes)
        ]

        for session_id in expired:
            self.delete_session(session_id)

        if expired:
            logger.info(f"Cleaned up {len(expired)} expired sessions")

        return len(expired)

    def get_active_session_count(self) -> int:
        """
        Get the number of active sessions.

        Returns:
            Number of active sessions
        """
        self.cleanup_expired_sessions()
        return len(self.sessions)
