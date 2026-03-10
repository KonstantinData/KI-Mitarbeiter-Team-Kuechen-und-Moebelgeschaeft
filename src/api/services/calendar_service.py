"""Google Calendar Service — Grundgerüst."""

import structlog

log = structlog.get_logger()


class CalendarService:
    """
    Google Calendar Integration.

    Wird implementiert wenn Max (Beratungs-Agent) gebaut wird.
    Ermöglicht: Freie Termine prüfen, Termin buchen, Termin stornieren.
    """

    async def get_free_slots(self, berater_id: str, date: str) -> list[dict]:
        """Gibt freie Terminslots für einen Berater zurück."""
        raise NotImplementedError("Google Calendar noch nicht implementiert")

    async def create_event(self, berater_id: str, event_data: dict) -> str:
        """Erstellt einen Kalender-Eintrag und gibt die Event-ID zurück."""
        raise NotImplementedError("Google Calendar noch nicht implementiert")

    async def delete_event(self, berater_id: str, event_id: str) -> None:
        """Löscht einen Kalender-Eintrag."""
        raise NotImplementedError("Google Calendar noch nicht implementiert")
