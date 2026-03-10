"""Pydantic Models für den Agent Core."""

from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field


class AgentContext(BaseModel):
    """Vollständiger Kontext für einen Agent-Aufruf."""

    studio_id: UUID
    conversation_id: UUID
    visitor_id: str
    messages: list[dict[str, Any]] = Field(default_factory=list)
    lead_summary: str | None = None
    knowledge_snippets: list[str] = Field(default_factory=list)
    studio_config: dict[str, Any] = Field(default_factory=dict)


class LLMResponse(BaseModel):
    """Antwort des LLM-Wrappers."""

    content: str
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    stop_reason: str = "end_turn"


class ToolResult(BaseModel):
    """Ergebnis einer Tool-Ausführung."""

    tool_name: str
    success: bool
    result: Any = None
    error: str | None = None


class ChatMessage(BaseModel):
    """Eingehende Chat-Nachricht über WebSocket."""

    content: str
    visitor_id: str
    studio_slug: str
