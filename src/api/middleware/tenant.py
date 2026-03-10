"""Multi-Tenant Middleware: Setzt studio_id aus Request-Header oder Query-Parameter."""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Multi-Tenant Middleware.

    Extrahiert die studio_id aus dem X-Studio-ID Header oder
    dem studio Query-Parameter und hängt sie an den Request-State.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """Extrahiert und setzt die Tenant-ID."""
        studio_id = (
            request.headers.get("X-Studio-ID")
            or request.query_params.get("studio_id")
        )
        request.state.studio_id = studio_id
        return await call_next(request)
