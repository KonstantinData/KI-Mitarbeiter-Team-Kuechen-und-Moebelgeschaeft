"""Claude API Wrapper mit Tool Use, Retry-Logic und Token-Tracking."""

import asyncio
from typing import Any

import structlog
from anthropic import AsyncAnthropic, APIStatusError, RateLimitError

from src.api.config import get_settings
from src.core.types import LLMResponse

log = structlog.get_logger()
settings = get_settings()


class LLMClient:
    """
    Wrapper um die Anthropic Claude API.

    - Unterstützt Tool Use (function calling)
    - Retry-Logic mit Exponential Backoff bei Rate-Limits
    - Token-Counting für Kostentracking
    - Prompt Caching für System-Prompts
    """

    def __init__(self) -> None:
        self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        self._model = settings.anthropic_model
        self._max_tokens = settings.anthropic_max_tokens

    async def chat(
        self,
        system_prompt: str,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        max_retries: int = 3,
    ) -> LLMResponse:
        """
        Ruft Claude auf und gibt eine strukturierte Antwort zurück.

        Retry-Logic bei RateLimitError mit Exponential Backoff.
        """
        for attempt in range(max_retries):
            try:
                kwargs: dict[str, Any] = {
                    "model": self._model,
                    "max_tokens": self._max_tokens,
                    "system": [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},
                        }
                    ],
                    "messages": messages,
                }
                if tools:
                    kwargs["tools"] = tools

                response = await self._client.messages.create(**kwargs)

                content_text = ""
                tool_calls: list[dict[str, Any]] = []

                for block in response.content:
                    if block.type == "text":
                        content_text = block.text
                    elif block.type == "tool_use":
                        tool_calls.append({
                            "id": block.id,
                            "name": block.name,
                            "input": block.input,
                        })

                log.info(
                    "llm.response",
                    model=self._model,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    stop_reason=response.stop_reason,
                )

                return LLMResponse(
                    content=content_text,
                    tool_calls=tool_calls,
                    input_tokens=response.usage.input_tokens,
                    output_tokens=response.usage.output_tokens,
                    stop_reason=response.stop_reason or "end_turn",
                )

            except RateLimitError:
                wait = 2**attempt
                log.warning("llm.rate_limit", attempt=attempt, wait=wait)
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait)
                else:
                    raise
            except APIStatusError as e:
                log.error("llm.api_error", status=e.status_code, message=str(e))
                raise

        msg = "Max Retries überschritten"
        raise RuntimeError(msg)
