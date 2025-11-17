"""
Configuration management for Conversational RAG system.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_temperature: float = 0.7  # Higher for conversational responses

    # Document Processing
    upload_directory: str = "./uploads"
    vectorstore_path: str = "./vectorstore"
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 10
    supported_extensions: list = [".pdf", ".txt", ".docx", ".md"]

    # Session Management
    session_timeout_minutes: int = 60
    max_history_messages: int = 20  # Maximum messages to keep in memory
    cleanup_interval_minutes: int = 10  # How often to cleanup expired sessions

    # Conversational Settings
    max_context_messages: int = 10  # Number of previous messages to include in context
    context_window_tokens: int = 3000  # Approximate token limit for context

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
