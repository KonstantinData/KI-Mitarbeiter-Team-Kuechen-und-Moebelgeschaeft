"""Resend E-Mail Service — Grundgerüst."""

import structlog

log = structlog.get_logger()


class EmailService:
    """
    E-Mail-Versand über Resend API.

    Wird implementiert wenn Bestätigungs- und Follow-up-E-Mails
    benötigt werden (ab Phase 5 mit Anna).
    """

    async def send(
        self,
        to: str,
        subject: str,
        html: str,
        from_name: str | None = None,
    ) -> str:
        """Sendet eine E-Mail und gibt die Message-ID zurück."""
        raise NotImplementedError("E-Mail-Service noch nicht implementiert")

    async def send_appointment_confirmation(
        self, to: str, appointment_data: dict
    ) -> str:
        """Sendet eine Terminbestätigung."""
        raise NotImplementedError("E-Mail-Service noch nicht implementiert")
