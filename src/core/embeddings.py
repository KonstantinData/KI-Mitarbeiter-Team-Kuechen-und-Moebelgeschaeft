"""OpenAI Embedding Wrapper für Vektorsuche."""

import structlog
from openai import AsyncOpenAI

from src.api.config import get_settings

log = structlog.get_logger()
settings = get_settings()


class EmbeddingClient:
    """
    Wrapper um die OpenAI Embeddings API.

    Nutzt text-embedding-3-small (1536 Dimensionen, günstig, bewährt).
    """

    def __init__(self) -> None:
        self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_embedding_model

    async def embed(self, text: str) -> list[float]:
        """Erstellt einen Embedding-Vektor für den gegebenen Text."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=text,
        )
        log.debug("embedding.created", model=self._model, text_len=len(text))
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Erstellt Embedding-Vektoren für mehrere Texte auf einmal."""
        response = await self._client.embeddings.create(
            model=self._model,
            input=texts,
        )
        return [item.embedding for item in response.data]
