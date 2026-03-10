"""Health-Check Endpoint."""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

from src.api.config import get_settings

router = APIRouter()
settings = get_settings()


class HealthResponse(BaseModel):
    """Antwort des Health-Check Endpoints."""

    status: str
    env: str
    timestamp: str
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check() -> HealthResponse:
    """Gibt den aktuellen Status der API zurück."""
    return HealthResponse(
        status="ok",
        env=settings.app_env,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
