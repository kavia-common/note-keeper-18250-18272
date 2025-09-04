"""
Application configuration and settings handling.

Loads environment variables and exposes settings used across the app
like database URL and JWT configuration.

Note: Do not hard-code secrets; use environment variables. See .env.example
for required variables.
"""
from functools import lru_cache
from pydantic import BaseModel, Field
import os


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    # FastAPI app metadata
    APP_NAME: str = Field(default="Notes API", description="Application name")
    APP_DESCRIPTION: str = Field(
        default="A FastAPI backend for a notes application with auth and CRUD.",
        description="Application description",
    )
    APP_VERSION: str = Field(default="1.0.0", description="Application version")

    # Database
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./notes.db"),
        description="SQLAlchemy database URL",
    )

    # JWT
    JWT_SECRET_KEY: str = Field(
        default=os.getenv("JWT_SECRET_KEY", "CHANGE_ME_DEV_ONLY"),
        description="Secret key for signing JWT tokens",
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")),
        description="Minutes until access tokens expire",
    )

    # CORS
    CORS_ALLOW_ORIGINS: str = Field(
        default=os.getenv("CORS_ALLOW_ORIGINS", "*"),
        description="Comma separated list of allowed CORS origins",
    )


# PUBLIC_INTERFACE
@lru_cache
def get_settings() -> Settings:
    """Return cached application settings instance."""
    return Settings()
