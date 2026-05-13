"""
Central configuration — single source of truth for all settings.
"""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve project root (parent of src/)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # API Keys
    GEMINI_API_KEY: str
    GITHUB_TOKEN: Optional[str] = None
    SERPER_API_KEY: Optional[str] = None

    # Model Configuration
    MODEL_NAME: str = "gemini-2.5-flash"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"

    # ATS Configuration
    ATS_THRESHOLD: int = 85
    MAX_OPTIMIZATION_LOOPS: int = 3

    # Infrastructure
    CACHE_DIR: str = "cache"
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE),
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()