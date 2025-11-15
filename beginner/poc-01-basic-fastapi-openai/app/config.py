"""
Configuration management for the application.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "POC 1: Basic FastAPI + OpenAI Integration"
    api_version: str = "1.0.0"
    api_description: str = "Simple REST API demonstrating FastAPI with OpenAI chat completion"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_timeout: int = 30

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
