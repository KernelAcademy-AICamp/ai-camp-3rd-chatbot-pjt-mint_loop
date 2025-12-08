"""Application settings management."""
import os
from functools import lru_cache
from pathlib import Path
from dotenv import load_dotenv


def _find_and_load_dotenv() -> bool:
    """Find and load .env file from parent directories."""
    current = Path(__file__).resolve().parent
    for _ in range(6):
        env_file = current / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            return True
        current = current.parent
    load_dotenv()
    return False


_find_and_load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    # Model settings
    TEXT_MODEL: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.0-flash")
    IMAGE_MODEL: str = os.getenv("GEMINI_IMAGE_MODEL", "imagen-3.0-generate-001")
    CHAT_MODEL: str = os.getenv("GEMINI_CHAT_MODEL", "gemini-2.0-flash")
    IMAGE_PROVIDER: str = os.getenv("IMAGE_PROVIDER", "gemini")

    # CORS settings
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
