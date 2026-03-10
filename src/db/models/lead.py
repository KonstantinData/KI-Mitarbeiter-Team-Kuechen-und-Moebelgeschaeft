"""SQLAlchemy Model für Interessenten (Leads)."""

import uuid
from typing import Any

from sqlalchemy import JSON, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base, TimestampMixin, UUIDMixin


class Lead(UUIDMixin, TimestampMixin, Base):
    """Ein erfasster Interessent."""

    __tablename__ = "leads"

    studio_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("studios.id", ondelete="CASCADE"),
        nullable=False,
    )
    visitor_id: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="new", nullable=False)
    score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    profile: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_channel: Mapped[str | None] = mapped_column(String(100), nullable=True)

    __table_args__ = (
        Index("ix_leads_studio_id", "studio_id"),
        Index("ix_leads_studio_status_score", "studio_id", "status", "score"),
    )

    def __repr__(self) -> str:
        return f"<Lead id={self.id} status={self.status!r} score={self.score}>"
