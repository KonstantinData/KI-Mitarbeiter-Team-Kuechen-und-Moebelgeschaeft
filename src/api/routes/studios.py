"""Route-Stub fuer Studios — wird mit den Agenten implementiert."""

from fastapi import APIRouter

router = APIRouter(prefix="/studios", tags=["Studios"])


@router.get("/")
async def list_stub() -> dict:
    """Noch nicht implementiert."""
    return {"detail": "Noch nicht implementiert", "status": 501}
