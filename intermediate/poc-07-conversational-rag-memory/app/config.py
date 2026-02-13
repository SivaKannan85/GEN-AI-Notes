"""Configuration for POC 7 service."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_title: str = "POC 7 - Conversational RAG with Memory"
    api_version: str = "1.0.0"
    api_description: str = "Session-aware conversational RAG demo"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
