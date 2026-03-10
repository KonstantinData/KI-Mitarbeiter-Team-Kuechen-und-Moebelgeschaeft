"""Tests für den LLM-Wrapper (mit Mocks — kein echter API-Call)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.core.types import LLMResponse


def test_llm_response_model():
    """LLMResponse kann korrekt instanziiert werden."""
    response = LLMResponse(
        content="Hallo!",
        tool_calls=[],
        input_tokens=10,
        output_tokens=5,
        stop_reason="end_turn",
    )
    assert response.content == "Hallo!"
    assert response.input_tokens == 10
    assert response.stop_reason == "end_turn"


@pytest.mark.asyncio
@patch("src.core.llm.AsyncAnthropic")
async def test_llm_client_chat(mock_anthropic_class):
    """LLMClient.chat() ruft die Anthropic API auf und gibt LLMResponse zurück."""
    # Mock aufbauen
    mock_message = MagicMock()
    mock_message.content = [MagicMock(type="text", text="Test-Antwort")]
    mock_message.usage.input_tokens = 20
    mock_message.usage.output_tokens = 10
    mock_message.stop_reason = "end_turn"

    mock_client = AsyncMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)
    mock_anthropic_class.return_value = mock_client

    from src.core.llm import LLMClient
    llm = LLMClient()
    llm._client = mock_client

    response = await llm.chat(
        system_prompt="Du bist ein Test-Agent.",
        messages=[{"role": "user", "content": "Hallo"}],
    )

    assert isinstance(response, LLMResponse)
    assert response.content == "Test-Antwort"
    assert response.input_tokens == 20
