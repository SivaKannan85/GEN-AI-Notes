"""
Configuration management for APM integration.
"""
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API Configuration
    api_title: str = "POC 5: Basic APM Integration"
    api_version: str = "1.0.0"
    api_description: str = "FastAPI application with ElasticAPM monitoring"

    # ElasticAPM Configuration
    elastic_apm_enabled: bool = True
    elastic_apm_service_name: str = "poc-05-apm-demo"
    elastic_apm_server_url: str = "http://localhost:8200"
    elastic_apm_environment: str = "development"
    elastic_apm_secret_token: str = ""  # Optional, for APM server authentication

    # APM Feature Flags
    apm_capture_body: str = "all"  # all, errors, transactions, off
    apm_capture_headers: bool = True
    apm_transaction_sample_rate: float = 1.0  # 1.0 = 100% of transactions
    apm_span_frames_min_duration: str = "5ms"  # Minimum duration to capture stack frames

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
