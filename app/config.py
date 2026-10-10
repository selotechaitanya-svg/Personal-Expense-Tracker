"""Application configuration settings loaded from environment variables."""

import os
from functools import lru_cache
from typing import List

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


class Settings:
    """Central configuration for application runtime, database, and security."""

    @property
    def database_url(self) -> str:
        """Return the database URL, normalizing legacy postgres:// prefixes for SQLAlchemy."""
        url = os.getenv("DATABASE_URL", "sqlite:///./expenses.db")
        # Cloud providers (Render, Heroku, Supabase, Neon) often use postgres://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url

    @property
    def environment(self) -> str:
        """Application runtime environment: development, staging, production, test."""
        return os.getenv("ENVIRONMENT", "development").lower()

    @property
    def host(self) -> str:
        """Host address to bind the server to."""
        return os.getenv("HOST", "0.0.0.0")

    @property
    def port(self) -> int:
        """Port number to bind the server to."""
        try:
            return int(os.getenv("PORT", "8000"))
        except ValueError:
            return 8000

    @property
    def cors_origins(self) -> List[str]:
        """Allowed CORS origins as a list of domain strings."""
        raw = os.getenv("CORS_ORIGINS", "*")
        if raw.strip() == "*":
            return ["*"]
        return [origin.strip() for origin in raw.split(",") if origin.strip()]

    @property
    def docs_enabled(self) -> bool:
        """Whether Swagger UI and ReDoc are enabled."""
        val = os.getenv("DOCS_ENABLED", "true").lower()
        return val in ("true", "1", "yes", "t")

    @property
    def log_level(self) -> str:
        """Application logging level."""
        return os.getenv("LOG_LEVEL", "INFO").upper()


@lru_cache()
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings."""
    return Settings()


settings = get_settings()
