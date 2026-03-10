"""Abstrakte Basisklasse für alle KI-Agenten."""

from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.knowledge import KnowledgeBase
from src.core.llm import LLMClient
from src.core.memory import MemoryManager
from src.core.tool_registry import ToolRegistry
from src.core.tool_runner import ToolRunner
from src.core.types import AgentContext, LLMResponse
from src.db.models.conversation import Conversation
from src.db.models.message import Message
from src.db.models.studio import Studio

log = structlog.get_logger()


class BaseAgent(ABC):
    """
    Abstrakte Basisklasse für alle KI-Agenten.

    Jeder Agent durchläuft bei einer eingehenden Nachricht
    den gleichen 7-Schritte-Prozess:
    1. Kontext laden (Studio, Lead, History)
    2. Absicht erkennen
    3. Wissen abrufen (Wissensbasis durchsuchen)
    4. Tools bereitstellen
    5. LLM aufrufen (Claude mit System-Prompt + Tools)
    6. Tool-Calls ausführen (falls vorhanden)
    7. Ergebnis speichern + zurückgeben

    Subklassen implementieren:
    - get_system_prompt() -> str
    - get_tools() -> ToolRegistry
    - get_knowledge_categories() -> list[str]
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._llm = LLMClient()
        self._memory = MemoryManager(session)
        self._knowledge = KnowledgeBase(session)

    @abstractmethod
    def get_system_prompt(
        self,
        studio: Studio,
        knowledge_snippets: list[str],
        lead_summary: str | None,
    ) -> str:
        """Gibt den System-Prompt für diesen Agenten zurück."""
        ...

    @abstractmethod
    def get_tools(self) -> ToolRegistry:
        """Gibt die Tool-Registry mit allen verfügbaren Tools zurück."""
        ...

    @abstractmethod
    def get_knowledge_categories(self) -> list[str]:
        """Gibt die Kategorien zurück, die dieser Agent in der Wissensbasis sucht."""
        ...

    async def process_message(
        self,
        user_message: str,
        conversation: Conversation,
        studio: Studio,
    ) -> str:
        """
        Der 7-Schritte-Loop. Wird von Subklassen NICHT überschrieben.

        Verarbeitet eine Nachricht und gibt die Antwort als String zurück.
        """
        log.info(
            "agent.process_message",
            studio=studio.slug,
            conversation_id=str(conversation.id),
        )

        # Schritt 1: Kontext laden
        context = await self._memory.get_context(conversation.id, studio.id)

        # Schritt 2+3: Wissen abrufen
        knowledge_chunks = await self._knowledge.search(
            query=user_message,
            studio_id=studio.id,
            categories=self.get_knowledge_categories(),
            limit=5,
        )
        knowledge_snippets = [
            f"**{chunk.title}**\n{chunk.content}" for chunk in knowledge_chunks
        ]

        # Schritt 4: System-Prompt aufbauen
        system_prompt = self.get_system_prompt(
            studio=studio,
            knowledge_snippets=knowledge_snippets,
            lead_summary=context.lead_summary,
        )

        # Schritt 5: LLM aufrufen
        tool_registry = self.get_tools()
        tool_runner = ToolRunner(tool_registry)
        messages = context.messages + [{"role": "user", "content": user_message}]

        response = await self._llm.chat(
            system_prompt=system_prompt,
            messages=messages,
            tools=tool_runner.get_tool_definitions() or None,
        )

        # Schritt 6: Tool-Calls ausführen (falls vorhanden)
        final_response = response
        if response.tool_calls:
            tool_results = await tool_runner.execute_all(response.tool_calls)
            # Claude nochmals aufrufen mit Tool-Ergebnissen
            messages_with_tools = messages + [
                {
                    "role": "assistant",
                    "content": [
                        {"type": "tool_use", "id": tc["id"], "name": tc["name"], "input": tc["input"]}
                        for tc in response.tool_calls
                    ],
                },
                {"role": "user", "content": tool_results},
            ]
            final_response = await self._llm.chat(
                system_prompt=system_prompt,
                messages=messages_with_tools,
            )

        # Schritt 7: Nachrichten speichern
        await self._save_message(conversation.id, "user", user_message)
        await self._save_message(
            conversation.id,
            "assistant",
            final_response.content,
            tool_calls=response.tool_calls if response.tool_calls else None,
            token_count=final_response.input_tokens + final_response.output_tokens,
        )

        return final_response.content

    async def _save_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        tool_calls: list[dict[str, Any]] | None = None,
        token_count: int | None = None,
    ) -> None:
        """Speichert eine Nachricht in der Datenbank."""
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tool_calls=tool_calls,
            token_count=token_count,
        )
        self._session.add(message)
