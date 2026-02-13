"""Configuration management for POC 6 multi-document-type RAG."""
from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API
    api_title: str = "POC 6: RAG System with Multiple Document Types"
    api_version: str = "1.0.0"
    api_description: str = "Production-ready RAG API with TXT/MD/PDF/DOCX ingestion and metadata filtering"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_embedding_model: str = "text-embedding-3-small"
    openai_timeout: int = 45

    # Document processing
    chunk_size: int = 1200
    chunk_overlap: int = 200
    separators: str = "\n\n|\n| |"

    # Retrieval and ranking
    default_top_k: int = 4
    max_top_k: int = 15

    # Vector store
    vector_store_path: str = "./vector_store"

    # Runtime
    max_upload_size_bytes: int = 15_000_000
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
