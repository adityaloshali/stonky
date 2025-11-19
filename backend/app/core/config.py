"""
Application configuration using Pydantic Settings.
Loads and validates environment variables.
"""

from typing import List
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    ENV: str = Field(default="development", description="Environment: development, staging, production")
    DEBUG: bool = Field(default=True, description="Debug mode")
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    API_V1_PREFIX: str = Field(default="/api/v1", description="API v1 prefix")

    # CORS
    CORS_ORIGINS: str = Field(
        default="http://localhost:3000,http://127.0.0.1:3000",
        description="Comma-separated list of allowed CORS origins"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS_ORIGINS string to list."""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    # Database
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://stonky:stonky@localhost:5432/stonky",
        description="PostgreSQL connection string (async)"
    )
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string"
    )
    REDIS_TOKEN: str | None = Field(default=None, description="Redis auth token (for managed Redis)")

    # Celery
    CELERY_BROKER_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Celery broker URL"
    )
    CELERY_RESULT_BACKEND: str = Field(
        default="redis://localhost:6379/0",
        description="Celery result backend URL"
    )

    # External Services
    SCREENER_COOKIE: str | None = Field(
        default=None,
        description="Screener.in session cookie (required for 10-year fundamentals)"
    )

    # AI/LLM
    OPENAI_API_KEY: str | None = Field(default=None, description="OpenAI API key")
    OPENROUTER_API_KEY: str | None = Field(default=None, description="OpenRouter API key")
    OPENAI_BASE_URL: str = Field(
        default="https://api.openai.com/v1",
        description="OpenAI API base URL"
    )
    AI_MODEL: str = Field(default="gpt-4o-mini", description="Default AI model")

    # Security
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-in-production",
        description="Secret key for JWT tokens"
    )
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=30,
        description="Access token expiration time in minutes"
    )

    # Cache TTL (Time To Live in seconds)
    CACHE_TTL_PRICES: int = Field(default=300, description="Price data cache TTL (5 min)")
    CACHE_TTL_NEWS: int = Field(default=600, description="News cache TTL (10 min)")
    CACHE_TTL_ANALYSIS: int = Field(default=86400, description="Analysis cache TTL (24 hours)")
    CACHE_TTL_FUNDAMENTALS: int = Field(
        default=604800,
        description="Fundamentals cache TTL (7 days)"
    )

    # Rate Limiting
    RATE_LIMIT_SCRAPER: int = Field(
        default=10,
        description="Max requests per minute to Screener.in"
    )
    RATE_LIMIT_NSE: int = Field(default=20, description="Max requests per minute to NSE")

    @validator("ENV")
    def validate_env(cls, v: str) -> str:
        """Validate ENV is one of allowed values."""
        allowed = ["development", "staging", "production"]
        if v not in allowed:
            raise ValueError(f"ENV must be one of {allowed}")
        return v

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate LOG_LEVEL is valid."""
        allowed = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed:
            raise ValueError(f"LOG_LEVEL must be one of {allowed}")
        return v.upper()

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.ENV == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.ENV == "production"

    @property
    def has_screener_cookie(self) -> bool:
        """Check if Screener.in cookie is configured."""
        return bool(self.SCREENER_COOKIE and len(self.SCREENER_COOKIE) > 0)

    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured."""
        return bool(self.OPENAI_API_KEY and len(self.OPENAI_API_KEY) > 0)

    @property
    def has_openrouter_key(self) -> bool:
        """Check if OpenRouter API key is configured."""
        return bool(self.OPENROUTER_API_KEY and len(self.OPENROUTER_API_KEY) > 0)


# Global settings instance
settings = Settings()
