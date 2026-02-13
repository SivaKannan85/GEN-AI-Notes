"""Configuration for POC 7 Conversational RAG with Memory."""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    api_title: str = "POC 7: Conversational RAG with Memory"
    api_version: str = "1.0.0"
    api_description: str = "Session-based conversational RAG API with FAISS retrieval"

    chunk_size: int = 800
    chunk_overlap: int = 150
    default_top_k: int = 3
    max_top_k: int = 10

    max_history_turns: int = 5

    enable_openai_generation: bool = False
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"

    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached settings instance."""
    return Settings()
