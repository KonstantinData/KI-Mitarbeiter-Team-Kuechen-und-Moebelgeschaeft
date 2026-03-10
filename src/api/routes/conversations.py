"""Route-Stub fuer Konversationen — wird mit den Agenten implementiert."""

from fastapi import APIRouter

router = APIRouter(prefix="/conversations", tags=["Konversationen"])


@router.get("/")
async def list_stub() -> dict:
    """Noch nicht implementiert."""
    return {"detail": "Noch nicht implementiert", "status": 501}
