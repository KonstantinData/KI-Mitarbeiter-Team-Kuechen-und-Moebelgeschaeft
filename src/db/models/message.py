"""SQLAlchemy Model für einzelne Nachrichten."""

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.base import Base, UUIDMixin, utcnow


class Message(UUIDMixin, Base):
    """Eine einzelne Nachricht in einer Konversation."""

    __tablename__ = "messages"

    conversation_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    tool_calls: Mapped[list | None] = mapped_column(JSON, nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    __table_args__ = (
        Index("ix_messages_conversation_created", "conversation_id", "created_at"),
    )

    def __repr__(self) -> str:
        return f"<Message id={self.id} role={self.role!r}>"
