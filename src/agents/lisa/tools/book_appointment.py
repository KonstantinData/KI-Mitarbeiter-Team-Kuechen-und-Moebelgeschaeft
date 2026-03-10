"""
Tool: book_appointment
======================
Lisa ruft dieses Tool auf, wenn der Kunde einem Beratungstermin zustimmt.

Aktueller Stand (Stub):
- Speichert den Terminwunsch als FollowUp in der DB
- Gibt eine Bestätigung zurück
- Google Calendar Integration folgt in einem separaten Schritt

Sobald Google Calendar angebunden ist:
- OAuth-Token des Studios laden
- Freie Slots abfragen
- Termin anlegen
- Terminbestätigung per E-Mail senden (via Resend)
"""

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tool_registry import BaseTool
from src.db.models.followup import FollowUp
from src.db.models.lead import Lead

log = structlog.get_logger()


class BookAppointmentTool(BaseTool):
    """
    Bucht einen Beratungstermin (aktuell als Stub — speichert FollowUp).

    Braucht DB-Session, Studio-ID und Conversation-ID —
    werden beim Initialisieren übergeben.
    """

    name = "book_appointment"
    description = (
        "Buche einen Beratungstermin, wenn der Kunde zustimmt. "
        "Übergib Wunschtermin (Datum/Uhrzeit als Text), Namen und Kontaktdaten. "
        "Der Termin wird gespeichert und das Studio-Team wird benachrichtigt."
    )
    input_schema = {
        "type": "object",
        "properties": {
            "wished_datetime": {
                "type": "string",
                "description": "Gewünschter Termin als Text (z.B. 'Mittwoch 16 Uhr', '15. April nachmittags')",
            },
            "customer_name": {
                "type": "string",
                "description": "Name des Kunden",
            },
            "customer_email": {
                "type": "string",
                "description": "E-Mail des Kunden für die Terminbestätigung",
            },
            "customer_phone": {
                "type": "string",
                "description": "Telefonnummer des Kunden",
            },
            "notes": {
                "type": "string",
                "description": "Besondere Wünsche oder Infos für den Berater",
            },
        },
        "required": ["wished_datetime"],
    }

    def __init__(
        self,
        session: AsyncSession,
        studio_id: UUID,
        visitor_id: str,
    ) -> None:
        self._session = session
        self._studio_id = studio_id
        self._visitor_id = visitor_id

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Speichert Terminwunsch als FollowUp und gibt Bestätigung zurück."""
        wished_datetime = kwargs.get("wished_datetime", "")
        customer_name = kwargs.get("customer_name", "")
        customer_email = kwargs.get("customer_email", "")
        notes = kwargs.get("notes", "")

        # Lead für diesen Besucher suchen
        result = await self._session.execute(
            select(Lead)
            .where(Lead.studio_id == self._studio_id)
            .where(Lead.visitor_id == self._visitor_id)
        )
        lead = result.scalar_one_or_none()

        if lead is None:
            log.warning("book_appointment.no_lead", visitor_id=self._visitor_id)
            return {
                "success": False,
                "message": (
                    "Kein Lead-Datensatz gefunden. "
                    "Bitte zuerst extract_lead_data aufrufen."
                ),
            }

        # Lead-Status auf "termin" setzen
        lead.status = "appointment"

        # FollowUp als Terminwunsch speichern
        content_parts = [f"Terminwunsch: {wished_datetime}"]
        if customer_name:
            content_parts.append(f"Kunde: {customer_name}")
        if customer_email:
            content_parts.append(f"E-Mail: {customer_email}")
        if notes:
            content_parts.append(f"Notizen: {notes}")

        followup = FollowUp(
            id=uuid.uuid4(),
            studio_id=self._studio_id,
            lead_id=lead.id,
            type="appointment_request",
            channel="widget",
            scheduled_at=datetime.now(timezone.utc) + timedelta(hours=1),
            content="\n".join(content_parts),
            status="pending",
            autonomy_level="manual",
        )
        self._session.add(followup)

        log.info(
            "book_appointment.saved",
            lead_id=str(lead.id),
            wished_datetime=wished_datetime,
        )

        # TODO: Google Calendar Integration
        # - OAuth-Token des Studios laden (lead.studio_id)
        # - Freie Slots abfragen via Google Calendar API
        # - Termin anlegen
        # - Terminbestätigung per Resend senden

        return {
            "success": True,
            "message": (
                f"Terminwunsch für '{wished_datetime}' wurde gespeichert. "
                "Das Studio-Team wird sich zur Bestätigung melden."
            ),
            "next_step": "google_calendar_not_connected",
        }
