"""Auth-Endpoints: Login und Token-Refresh."""

from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, HTTPException, status
from jose import jwt
from pydantic import BaseModel

from src.api.config import get_settings

router = APIRouter(prefix="/auth", tags=["Auth"])
settings = get_settings()


class LoginRequest(BaseModel):
    """Login-Anfrage mit Benutzername und Passwort."""

    username: str
    password: str


class TokenResponse(BaseModel):
    """JWT-Token-Antwort."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int


def _hash_password(password: str) -> bytes:
    """Erzeugt einen bcrypt-Hash für das gegebene Passwort."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def _verify_password(password: str, hashed: bytes) -> bool:
    """Vergleicht ein Passwort mit einem bcrypt-Hash."""
    return bcrypt.checkpw(password.encode(), hashed)


# Demo-User für Entwicklung — in Produktion aus DB laden
# Hash für "secret" — bei Programmstart generiert
_ADMIN_HASH = bcrypt.hashpw(b"secret", bcrypt.gensalt())
DEMO_USERS: dict[str, bytes] = {
    "admin": _ADMIN_HASH,
}


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """
    Authentifiziert einen Benutzer und gibt einen JWT-Token zurück.

    Demo-Credentials: admin / secret
    In Produktion: Benutzer aus DB laden + bcrypt verifizieren.
    """
    hashed = DEMO_USERS.get(request.username)
    if not hashed or not _verify_password(request.password, hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Ungültige Anmeldedaten",
            headers={"WWW-Authenticate": "Bearer"},
        )

    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    token = jwt.encode(
        {"sub": request.username, "exp": expire},
        settings.jwt_secret,
        algorithm=settings.jwt_algorithm,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_expire_minutes * 60,
    )
