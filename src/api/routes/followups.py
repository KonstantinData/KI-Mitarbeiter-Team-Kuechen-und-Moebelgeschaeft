"""Route-Stub fuer Follow-ups — wird mit den Agenten implementiert."""

from fastapi import APIRouter

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


@router.get("/")
async def list_stub() -> dict:
    """Noch nicht implementiert."""
    return {"detail": "Noch nicht implementiert", "status": 501}
