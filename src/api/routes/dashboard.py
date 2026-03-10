"""Route-Stub fuer Dashboard — wird mit den Agenten implementiert."""

from fastapi import APIRouter

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/")
async def list_stub() -> dict:
    """Noch nicht implementiert."""
    return {"detail": "Noch nicht implementiert", "status": 501}
