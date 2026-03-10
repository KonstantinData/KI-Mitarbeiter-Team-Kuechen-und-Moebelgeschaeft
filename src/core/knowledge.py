"""Wissensbasis-Suche mit pgvector für semantische Ähnlichkeitssuche."""

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.embeddings import EmbeddingClient
from src.db.models.knowledge_chunk import KnowledgeChunk

log = structlog.get_logger()


class KnowledgeBase:
    """
    Semantische Suche in der Wissensbasis eines Studios.

    Nutzt pgvector für Ähnlichkeitssuche:
    1. Nachricht wird embedded (OpenAI)
    2. Ähnlichste Chunks aus knowledge_chunks werden geladen
    3. Top-K Ergebnisse werden als Kontext zurückgegeben
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._embeddings = EmbeddingClient()

    async def search(
        self,
        query: str,
        studio_id: UUID,
        categories: list[str] | None = None,
        limit: int = 5,
    ) -> list[KnowledgeChunk]:
        """
        Sucht semantisch ähnliche Chunks für die gegebene Query.

        Gibt die Top-K ähnlichsten Chunks zurück.
        """
        query_embedding = await self._embeddings.embed(query)

        stmt = (
            select(KnowledgeChunk)
            .where(KnowledgeChunk.studio_id == studio_id)
            .where(KnowledgeChunk.embedding.isnot(None))
        )

        if categories:
            stmt = stmt.where(KnowledgeChunk.category.in_(categories))

        # Cosine Distanz für Sortierung (pgvector: <=> Operator)
        stmt = stmt.order_by(
            KnowledgeChunk.embedding.cosine_distance(query_embedding)
        ).limit(limit)

        result = await self._session.execute(stmt)
        chunks = result.scalars().all()

        log.info(
            "knowledge.search",
            query_len=len(query),
            studio_id=str(studio_id),
            results=len(chunks),
        )
        return list(chunks)

    async def add_chunk(
        self,
        studio_id: UUID,
        category: str,
        title: str,
        content: str,
        metadata: dict | None = None,
    ) -> KnowledgeChunk:
        """Fügt einen neuen Wissens-Chunk mit Embedding hinzu."""
        embedding = await self._embeddings.embed(f"{title}\n\n{content}")

        chunk = KnowledgeChunk(
            studio_id=studio_id,
            category=category,
            title=title,
            content=content,
            embedding=embedding,
            metadata_=metadata,
        )
        self._session.add(chunk)
        log.info("knowledge.chunk_added", title=title, category=category)
        return chunk
