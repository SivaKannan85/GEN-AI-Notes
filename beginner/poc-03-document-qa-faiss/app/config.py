"""
Configuration management for Document QA system.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "POC 3: Document QA with FAISS"
    api_version: str = "1.0.0"
    api_description: str = "Document question-answering system using FAISS and LangChain"

    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-3.5-turbo"
    openai_embedding_model: str = "text-embedding-ada-002"
    openai_timeout: int = 30

    # Document Processing Configuration
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # FAISS Configuration
    vector_store_path: str = "./vector_store"

    # Retrieval Configuration
    default_top_k: int = 3
    similarity_threshold: float = 0.7

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
