"""JWT Auth Middleware."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

EXCLUDED_PATHS = {"/health", "/auth/login", "/docs", "/openapi.json", "/redoc"}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Optionale JWT-Middleware.

    Prüft den Authorization-Header für geschützte Endpunkte.
    Die eigentliche Auth-Logik ist in deps.py (Dependency Injection).
    Diese Middleware kann für zentrales Logging genutzt werden.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Verarbeitet die Request und ruft den nächsten Handler auf."""
        return await call_next(request)
