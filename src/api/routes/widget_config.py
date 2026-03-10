"""Route-Stub fuer Widget-Konfiguration — wird mit den Agenten implementiert."""

from fastapi import APIRouter

router = APIRouter(prefix="/widget-config", tags=["Widget-Konfiguration"])


@router.get("/")
async def list_stub() -> dict:
    """Noch nicht implementiert."""
    return {"detail": "Noch nicht implementiert", "status": 501}
