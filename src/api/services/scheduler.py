"""APScheduler Cron-Jobs — Grundgerüst."""

import structlog
from apscheduler.schedulers.asyncio import AsyncIOScheduler

log = structlog.get_logger()

scheduler = AsyncIOScheduler()


def setup_scheduler() -> None:
    """Richtet die geplanten Jobs ein und startet den Scheduler."""
    # TODO: Jobs hinzufügen wenn Follow-up-Logik implementiert wird
    # Beispiel:
    # scheduler.add_job(check_followups, "interval", minutes=5)
    scheduler.start()
    log.info("scheduler.started")


def shutdown_scheduler() -> None:
    """Stoppt den Scheduler sauber."""
    if scheduler.running:
        scheduler.shutdown()
        log.info("scheduler.stopped")
