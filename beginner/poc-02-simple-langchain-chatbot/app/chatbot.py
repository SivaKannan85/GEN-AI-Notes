"""
LangChain chatbot implementation with conversation memory.
"""
import logging
from typing import Dict
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.config import get_settings
from app.session_manager import get_session_manager

logger = logging.getLogger(__name__)


class LangChainChatbot:
    """LangChain-powered chatbot with conversation memory."""

    def __init__(self):
        """Initialize the chatbot."""
        self.settings = get_settings()
        self.session_manager = get_session_manager()

        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            model=self.settings.openai_model,
            temperature=0.7,
            openai_api_key=self.settings.openai_api_key,
            request_timeout=self.settings.openai_timeout
        )

        # Define the conversation prompt template
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful and friendly AI assistant.
Your goal is to provide accurate, helpful, and engaging responses to user queries.
Be conversational and maintain context from previous messages in the conversation."""),
            MessagesPlaceholder(variable_name=self.settings.memory_key),
            ("human", "{input}")
        ])

    def chat(self, session_id: str, message: str, temperature: float = 0.7) -> Dict:
        """
        Process a chat message and return a response.

        Args:
            session_id: Unique session identifier
            message: User's message
            temperature: Sampling temperature for the LLM

        Returns:
            Dictionary containing response and metadata
        """
        logger.info(f"Processing message for session {session_id}")

        # Get or create session memory
        memory = self.session_manager.get_or_create_session(session_id)

        # Update LLM temperature if different
        if temperature != self.llm.temperature:
            self.llm.temperature = temperature

        # Create conversation chain with memory
        conversation = ConversationChain(
            llm=self.llm,
            memory=memory,
            prompt=self.prompt,
            verbose=False
        )

        # Get response from the chain
        response = conversation.predict(input=message)

        # Update session activity
        self.session_manager.update_session_activity(session_id)

        # Get conversation history
        messages = memory.chat_memory.messages

        # Convert messages to dict format
        conversation_history = [
            {
                "role": "user" if msg.type == "human" else "assistant",
                "content": msg.content,
                "timestamp": None  # LangChain messages don't have timestamps by default
            }
            for msg in messages
        ]

        # Estimate token usage (rough approximation)
        total_chars = sum(len(msg["content"]) for msg in conversation_history)
        estimated_tokens = total_chars // 4  # Rough approximation: 1 token ≈ 4 characters

        logger.info(f"Response generated for session {session_id}, estimated tokens: {estimated_tokens}")

        return {
            "response": response,
            "conversation_history": conversation_history,
            "tokens_used": estimated_tokens
        }


# Global chatbot instance
_chatbot: LangChainChatbot = None


def get_chatbot() -> LangChainChatbot:
    """Get the global chatbot instance."""
    global _chatbot
    if _chatbot is None:
        _chatbot = LangChainChatbot()
    return _chatbot
