"""
Google Calendar OAuth Routes
==============================
Ermöglicht Studio-Admins, ihren Google Calendar mit dem System zu verbinden.

Ablauf:
1. Admin ruft GET /google-calendar/connect?berater_id=<uuid> auf
2. Wird zu Google OAuth weitergeleitet
3. Nach Zustimmung: Google leitet zu /google-calendar/callback zurück
4. Callback tauscht Code gegen Tokens und speichert sie in Berater.calendar_tokens
5. Ab jetzt kann book_appointment echte Kalendereinträge erstellen

Endpunkte:
- GET /google-calendar/connect      → OAuth-URL generieren & weiterleiten
- GET /google-calendar/callback     → Code einlösen, Tokens speichern
- GET /google-calendar/status/{id}  → Verbindungsstatus eines Beraters prüfen
- DELETE /google-calendar/disconnect/{id} → Tokens löschen
"""

import uuid
from datetime import datetime, timezone

import structlog
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.google_calendar import build_auth_url, exchange_code_for_tokens
from src.db.database import get_session
from src.db.models.berater import Berater

log = structlog.get_logger()
router = APIRouter(prefix="/google-calendar", tags=["Google Calendar"])


# ──────────────────────────────────────────────────────────────────────────────
# OAuth initiieren
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/connect")
async def start_oauth(
    berater_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> RedirectResponse:
    """
    Startet den Google OAuth-Flow für einen Berater.

    Leitet den Admin direkt zu Google weiter.
    Nach der Zustimmung landet Google am /callback-Endpoint.
    """
    # Prüfen ob Berater existiert
    result = await session.execute(select(Berater).where(Berater.id == berater_id))
    berater = result.scalar_one_or_none()
    if not berater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Berater {berater_id} nicht gefunden",
        )

    # berater_id als state mitgeben → kommt im Callback zurück
    auth_url = build_auth_url(state=str(berater_id))
    log.info("google_calendar.oauth_started", berater_id=str(berater_id))
    return RedirectResponse(url=auth_url)


# ──────────────────────────────────────────────────────────────────────────────
# OAuth Callback
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/callback")
async def oauth_callback(
    code: str,
    state: str,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """
    Google leitet nach der Zustimmung hierher mit code + state zurück.

    Tauscht den Code gegen Tokens und speichert sie im Berater-Datensatz.
    """
    # state enthält die berater_id
    try:
        berater_id = uuid.UUID(state)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ungültiger state-Parameter",
        )

    result = await session.execute(select(Berater).where(Berater.id == berater_id))
    berater = result.scalar_one_or_none()
    if not berater:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Berater {berater_id} nicht gefunden",
        )

    # Code gegen Tokens tauschen
    try:
        tokens = exchange_code_for_tokens(code)
    except Exception as e:
        log.error("google_calendar.token_exchange_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token-Exchange fehlgeschlagen: {e}",
        )

    # Tokens + Zeitstempel in DB speichern
    tokens["connected_at"] = datetime.now(timezone.utc).isoformat()
    berater.calendar_tokens = tokens
    berater.calendar_provider = "google"

    log.info(
        "google_calendar.oauth_completed",
        berater_id=str(berater_id),
        berater_name=berater.name,
    )

    return {
        "success": True,
        "message": f"Google Calendar für {berater.name} erfolgreich verbunden.",
        "berater_id": str(berater_id),
    }


# ──────────────────────────────────────────────────────────────────────────────
# Status & Disconnect
# ──────────────────────────────────────────────────────────────────────────────


@router.get("/status/{berater_id}")
async def calendar_status(
    berater_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Gibt den Verbindungsstatus des Google Calendars zurück."""
    result = await session.execute(select(Berater).where(Berater.id == berater_id))
    berater = result.scalar_one_or_none()
    if not berater:
        raise HTTPException(status_code=404, detail="Berater nicht gefunden")

    connected = (
        berater.calendar_provider == "google"
        and berater.calendar_tokens is not None
        and "refresh_token" in (berater.calendar_tokens or {})
    )

    return {
        "berater_id": str(berater_id),
        "berater_name": berater.name,
        "calendar_connected": connected,
        "calendar_provider": berater.calendar_provider,
        "connected_at": (berater.calendar_tokens or {}).get("connected_at"),
    }


@router.delete("/disconnect/{berater_id}")
async def disconnect_calendar(
    berater_id: uuid.UUID,
    session: AsyncSession = Depends(get_session),
) -> dict:
    """Löscht die Google Calendar Verbindung eines Beraters."""
    result = await session.execute(select(Berater).where(Berater.id == berater_id))
    berater = result.scalar_one_or_none()
    if not berater:
        raise HTTPException(status_code=404, detail="Berater nicht gefunden")

    berater.calendar_tokens = None
    berater.calendar_provider = None

    log.info("google_calendar.disconnected", berater_id=str(berater_id))
    return {"success": True, "message": f"Google Calendar für {berater.name} getrennt."}
