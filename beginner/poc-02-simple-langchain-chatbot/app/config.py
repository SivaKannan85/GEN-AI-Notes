"""
Configuration management for the LangChain chatbot.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "POC 2: Simple LangChain Chatbot"
    api_version: str = "1.0.0"
    api_description: str = "LangChain-powered chatbot with conversation memory"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_timeout: int = 30

    # LangChain Configuration
    max_token_limit: int = 4000
    memory_key: str = "chat_history"

    # Session Management
    session_timeout_minutes: int = 30
    max_sessions: int = 100

    # Application Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()
