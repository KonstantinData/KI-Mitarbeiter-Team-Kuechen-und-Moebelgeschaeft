"""Rate Limiting Middleware: Begrenzt Anfragen pro IP."""

import time
from collections import defaultdict

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

# Maximale Anfragen pro Zeitfenster
MAX_REQUESTS = 60
WINDOW_SECONDS = 60


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Einfaches In-Memory Rate Limiting pro IP-Adresse.

    In Produktion: Redis-basiertes Rate Limiting verwenden.
    """

    def __init__(self, app) -> None:
        super().__init__(app)
        # ip → [timestamp, timestamp, ...]
        self._requests: dict[str, list[float]] = defaultdict(list)

    async def dispatch(self, request: Request, call_next) -> Response:
        """Prüft Rate Limit und gibt 429 zurück wenn überschritten."""
        client_ip = request.client.host if request.client else "unknown"
        now = time.time()
        window_start = now - WINDOW_SECONDS

        # Alte Einträge bereinigen
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        if len(self._requests[client_ip]) >= MAX_REQUESTS:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"detail": "Zu viele Anfragen. Bitte warte kurz."},
            )

        self._requests[client_ip].append(now)
        return await call_next(request)
