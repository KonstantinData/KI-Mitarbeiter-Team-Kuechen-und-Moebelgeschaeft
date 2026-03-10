"""SQLAlchemy Model für Küchenstudios."""

import uuid
from typing import Any

from sqlalchemy import JSON, Index, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base, TimestampMixin, UUIDMixin


class Studio(UUIDMixin, TimestampMixin, Base):
    """Ein Küchenstudio, das die Plattform nutzt."""

    __tablename__ = "studios"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    config: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    api_key: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    __table_args__ = (Index("ix_studios_slug", "slug"),)

    def __repr__(self) -> str:
        return f"<Studio id={self.id} slug={self.slug!r}>"
