"""
Configuration management for Pydantic AI Structuring.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "POC 4: Pydantic AI Response Structuring"
    api_version: str = "1.0.0"
    api_description: str = "Structured output extraction using Pydantic and OpenAI function calling"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo-1106"  # Supports function calling
    openai_timeout: int = 30
    temperature: float = 0.0  # Use 0 for deterministic extraction

    # Application Configuration
    log_level: str = "INFO"
    default_confidence_threshold: float = 0.7

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
