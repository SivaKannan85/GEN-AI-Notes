"""
Configuration management for LangChain Agents system.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings."""

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_temperature: float = 0.0  # Low temperature for precise reasoning

    # Agent Configuration
    max_iterations: int = 10
    agent_verbose: bool = True
    agent_early_stopping_method: str = "generate"  # or "force"

    # Tool Configuration
    enable_calculator: bool = True
    enable_datetime: bool = True
    enable_string_tools: bool = True
    enable_file_tools: bool = True
    enable_web_search: bool = False  # Requires additional API keys

    # API Configuration
    api_timeout_seconds: int = 60

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
