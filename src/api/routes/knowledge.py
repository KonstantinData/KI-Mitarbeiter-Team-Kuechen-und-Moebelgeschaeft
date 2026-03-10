"""Route-Stub fuer Wissensbasis — wird mit den Agenten implementiert."""

from fastapi import APIRouter

router = APIRouter(prefix="/knowledge", tags=["Wissensbasis"])


@router.get("/")
async def list_stub() -> dict:
    """Noch nicht implementiert."""
    return {"detail": "Noch nicht implementiert", "status": 501}
