"""
Configuration for RAG system with multiple document types.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List


class Settings(BaseSettings):
    """Application settings."""

    # API Configuration
    api_title: str = "POC 6: RAG System with Multiple Document Types"
    api_version: str = "1.0.0"
    api_description: str = "Advanced RAG system supporting PDF, TXT, DOCX, and Markdown files"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_timeout: int = 30

    # Document Processing
    chunk_size: int = 1000
    chunk_overlap: int = 200
    max_file_size_mb: int = 10

    # Supported file types
    supported_extensions: List[str] = [".pdf", ".txt", ".docx", ".md", ".markdown"]

    # Storage Paths
    upload_directory: str = "./uploads"
    vector_store_path: str = "./vector_store"

    # FAISS Configuration
    default_top_k: int = 4
    similarity_threshold: float = 0.7

    # Application Configuration
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
