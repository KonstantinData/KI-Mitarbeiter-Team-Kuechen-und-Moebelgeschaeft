"""Gemeinsame Basisklasse und Mixins für alle SQLAlchemy Models."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Gibt die aktuelle UTC-Zeit zurück."""
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    """Deklarative Basisklasse für alle Models."""


class TimestampMixin:
    """Mixin mit created_at und updated_at Feldern."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        onupdate=utcnow,
        nullable=False,
    )


class UUIDMixin:
    """Mixin mit UUID als Primary Key."""

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
