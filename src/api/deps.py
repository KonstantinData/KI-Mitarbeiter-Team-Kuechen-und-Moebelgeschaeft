"""Dependency Injection für FastAPI: DB-Session, Auth."""

from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.config import get_settings
from src.db.database import get_session

settings = get_settings()
security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency: Gibt eine Datenbank-Session zurück."""
    async for session in get_session():
        yield session


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> dict:
    """
    Dependency: Prüft JWT-Token und gibt den aktuellen User zurück.

    Wirft 401 wenn der Token fehlt oder ungültig ist.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nicht authentifiziert",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Ungültiger Token",
            )
        return {"user_id": user_id, "payload": payload}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültiger Token",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Typen für Dependency Injection
DBSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[dict, Depends(get_current_user)]
