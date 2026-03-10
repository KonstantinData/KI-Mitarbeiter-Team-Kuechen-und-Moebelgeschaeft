"""
Application Configuration
=========================
What:    Pydantic settings model for all environment variables.
Does:    Loads and validates configuration from .env file; provides type-safe access to settings.
Why:     Centralizes configuration; ensures required variables are present; prevents runtime errors.
Who:     All modules that need configuration (API, agents, services).
Depends: pydantic, pydantic-settings
"""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Lädt alle Umgebungsvariablen aus .env mit Validierung.
    Wenn eine Pflicht-Variable fehlt, crasht die App sofort
    mit einer klaren Fehlermeldung.
    """

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # Server
    app_env: str = "development"
    app_port: int = 8000
    app_host: str = "0.0.0.0"
    log_level: str = "DEBUG"

    # Datenbank
    database_url: str = "postgresql+asyncpg://ki_team:passwort@localhost:5432/ki_mitarbeiter"

    # Anthropic Claude
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_max_tokens: int = 1024

    # OpenAI Embeddings
    openai_api_key: str = ""
    openai_embedding_model: str = "text-embedding-3-small"

    # Resend E-Mail
    resend_api_key: str = ""
    resend_from_email: str = "noreply@example.com"
    resend_from_name: str = "KI-Assistent"

    # Google Calendar OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"

    # Auth (Dashboard)
    jwt_secret: str = "dev-secret-min-32-chars-placeholder!"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 10080

    # Encryption
    encryption_key: str = ""

    # URLs
    api_url: str = "http://localhost:8000"
    ws_url: str = "ws://localhost:8000"
    dashboard_url: str = "http://localhost:5173"
    widget_url: str = "http://localhost:5174"
    website_url: str = "https://www.mein-kuechenexperte.de"

    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list) -> list[str]:
        """Parst CORS_ORIGINS aus JSON-String oder Liste."""
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v


@lru_cache
def get_settings() -> Settings:
    """Gibt eine gecachte Settings-Instanz zurück."""
    return Settings()
