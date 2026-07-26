"""Provider-sideband provenance for Liquisto Voice navigation."""

from __future__ import annotations

import asyncio
import json
import secrets
from dataclasses import dataclass
from typing import Annotated, Any, Literal, Protocol
from urllib.parse import quote, urlsplit

import httpx
import structlog
from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, ValidationError
from websockets.asyncio.client import ClientConnection, connect
from websockets.exceptions import WebSocketException

from src.agents.liquisto_assistant.navigation import (
    IDENTIFIER_PATTERN,
    NAVIGATION_TOOL_NAME,
    LiquistoNavigationDecision,
    LiquistoNavigationRuntimeAttestation,
    LiquistoNavigationToolArguments,
    VoiceSessionId,
)
from src.api.config import Settings

log = structlog.get_logger()
ATTESTATION_PATH = "/internal/v1/assistant/navigation/attestations"
PRODUCTION_ATTESTATION_URL = (
    "http://liquisto-crm-service:8080"
    "/internal/v1/assistant/navigation/attestations"
)
PROVIDER_SIDEBAND_URL = "wss://api.openai.com/v1/realtime"
LOOPBACK_HOSTS = {"localhost", "127.0.0.1", "::1"}
MIN_RUNTIME_TOKEN_BYTES = 32
MAX_PROVIDER_EVENT_BYTES = 32_768
Identifier = Annotated[
    str,
    Field(min_length=1, max_length=200, pattern=IDENTIFIER_PATTERN),
]
voice_session_id_adapter = TypeAdapter(VoiceSessionId)


class NavigationSidebandError(RuntimeError):
    """Raised when provider provenance cannot be established fail-closed."""


class NavigationAttestationDeliveryError(NavigationSidebandError):
    """Raised when the tenant-local CRM does not persist an attestation."""

    def __init__(
        self,
        reason: str,
        *,
        attempt_count: int | None = None,
        retry_count: int | None = None,
        http_status: int | None = None,
        exception_class: str | None = None,
    ) -> None:
        super().__init__(reason)
        self.attempt_count = attempt_count
        self.retry_count = retry_count
        self.http_status = http_status
        self.exception_class = exception_class


class ProviderNavigationEvent(BaseModel):
    """Provider fields required from the authenticated monitoring connection."""

    model_config = ConfigDict(extra="ignore", frozen=True)

    event_id: Identifier
    type: Literal["response.function_call_arguments.done"]
    name: Literal["open_liquisto_destination"]
    call_id: Identifier
    arguments: str = Field(min_length=2, max_length=16_384)


@dataclass(frozen=True)
class NavigationSidebandContext:
    """Server-bound call context; no browser-controlled identity is accepted."""

    voice_session_id: str
    request_id: str


@dataclass(frozen=True)
class NavigationSidebandConfig:
    """Validated provider-monitoring and Runtime-to-CRM configuration."""

    attestation_url: str
    runtime_token: str
    delivery_timeout_seconds: float

    @classmethod
    def from_settings(cls, settings: Settings) -> NavigationSidebandConfig:
        if not settings.liquisto_navigation_sideband_enabled:
            raise NavigationSidebandError("navigation_sideband_disabled")
        token = settings.liquisto_olivia_navigation_runtime_token
        if (
            len(token.encode("utf-8")) < MIN_RUNTIME_TOKEN_BYTES
            or any(character.isspace() for character in token)
        ):
            raise NavigationSidebandError("navigation_runtime_token_invalid")
        if any(
            other and secrets.compare_digest(token, other)
            for other in (
                settings.liquisto_assistant_service_token,
                settings.openai_api_key,
            )
        ):
            raise NavigationSidebandError("navigation_runtime_token_not_dedicated")
        return cls(
            attestation_url=validate_attestation_url(
                settings.liquisto_olivia_navigation_attestation_url,
                app_env=settings.app_env,
            ),
            runtime_token=token,
            delivery_timeout_seconds=5.0,
        )


def validate_attestation_url(raw_url: str, *, app_env: str) -> str:
    """Allows only the fixed CRM endpoint or loopback with the identical path."""

    normalized = raw_url.strip()
    if not normalized:
        raise NavigationSidebandError("navigation_attestation_url_missing")
    try:
        parsed = urlsplit(normalized)
        _ = parsed.port
    except ValueError as exc:
        raise NavigationSidebandError("navigation_attestation_url_invalid") from exc
    if (
        parsed.scheme != "http"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path != ATTESTATION_PATH
    ):
        raise NavigationSidebandError("navigation_attestation_url_invalid")
    if app_env.lower() in {"development", "test"}:
        if parsed.hostname not in LOOPBACK_HOSTS:
            raise NavigationSidebandError("navigation_attestation_host_not_loopback")
        return normalized
    if normalized != PRODUCTION_ATTESTATION_URL:
        raise NavigationSidebandError("navigation_attestation_host_not_internal")
    return normalized


class AttestationSender(Protocol):
    async def deliver(
        self, attestation: LiquistoNavigationRuntimeAttestation
    ) -> LiquistoNavigationDecision: ...


class NavigationAttestationClient:
    """Posts one exact attestation over the dedicated server-only channel."""

    def __init__(self, config: NavigationSidebandConfig) -> None:
        self._config = config

    async def deliver(
        self, attestation: LiquistoNavigationRuntimeAttestation
    ) -> LiquistoNavigationDecision:
        headers = {
            "Authorization": f"Bearer {self._config.runtime_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        last_error: Exception | None = None
        attempts_made = 0
        for attempt in range(3):
            attempts_made = attempt + 1
            try:
                async with httpx.AsyncClient(
                    timeout=self._config.delivery_timeout_seconds,
                    follow_redirects=False,
                ) as client:
                    response = await client.post(
                        self._config.attestation_url,
                        headers=headers,
                        json=attestation.model_dump(mode="json"),
                    )
                response.raise_for_status()
                decision = LiquistoNavigationDecision.model_validate(response.json())
                if (
                    decision.request_id != attestation.request_id
                    or decision.call_id != attestation.call_id
                    or decision.destination_id != attestation.destination_id
                ):
                    raise NavigationAttestationDeliveryError(
                        "navigation_attestation_decision_mismatch"
                    )
                return decision
            except (
                httpx.HTTPError,
                ValidationError,
                ValueError,
                NavigationAttestationDeliveryError,
            ) as exc:
                last_error = exc
                if attempt < 2:
                    await asyncio.sleep(0.1 * (2**attempt))
        http_status = (
            last_error.response.status_code
            if isinstance(last_error, httpx.HTTPStatusError)
            else None
        )
        raise NavigationAttestationDeliveryError(
            "navigation_attestation_delivery_failed",
            attempt_count=attempts_made,
            retry_count=max(0, attempts_made - 1),
            http_status=http_status,
            exception_class=type(last_error).__name__ if last_error else None,
        ) from last_error


def build_runtime_attestation(
    *, raw_event: str | bytes, context: NavigationSidebandContext
) -> LiquistoNavigationRuntimeAttestation | None:
    """Returns an attestation only for the one accepted provider event and tool."""

    if isinstance(raw_event, bytes):
        if len(raw_event) > MAX_PROVIDER_EVENT_BYTES:
            raise NavigationSidebandError("provider_navigation_event_too_large")
        try:
            raw_event = raw_event.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise NavigationSidebandError("provider_navigation_event_invalid") from exc
    elif len(raw_event.encode("utf-8")) > MAX_PROVIDER_EVENT_BYTES:
        raise NavigationSidebandError("provider_navigation_event_too_large")
    try:
        candidate: Any = json.loads(raw_event)
    except json.JSONDecodeError as exc:
        raise NavigationSidebandError("provider_navigation_event_invalid") from exc
    if not isinstance(candidate, dict):
        raise NavigationSidebandError("provider_navigation_event_invalid")
    if candidate.get("type") != "response.function_call_arguments.done":
        return None
    if candidate.get("name") != NAVIGATION_TOOL_NAME:
        raise NavigationSidebandError("provider_navigation_tool_denied")
    try:
        event = ProviderNavigationEvent.model_validate(candidate)
        arguments = LiquistoNavigationToolArguments.model_validate_json(event.arguments)
    except ValidationError as exc:
        raise NavigationSidebandError("provider_navigation_event_invalid") from exc
    if arguments.request_id != context.request_id:
        raise NavigationSidebandError("provider_navigation_request_mismatch")
    return LiquistoNavigationRuntimeAttestation(
        contract_version="1.2",
        provider_event_type=event.type,
        tool_name=event.name,
        voice_session_id=context.voice_session_id,
        call_id=event.call_id,
        request_id=arguments.request_id,
        tenant_id=arguments.tenant_id,
        agent_id=arguments.agent_id,
        source=arguments.source,
        intent=arguments.intent,
        destination_id=arguments.destination_id,
        parameters=arguments.parameters,
    )


class LiquistoNavigationSidebandManager:
    """Owns authenticated monitoring connections for active Olivia calls."""

    def __init__(self) -> None:
        self._tasks: set[asyncio.Task[None]] = set()

    async def start(
        self,
        *,
        settings: Settings,
        voice_session_id: str,
        request_id: str,
    ) -> None:
        config = NavigationSidebandConfig.from_settings(settings)
        try:
            validated_voice_session_id = voice_session_id_adapter.validate_python(
                voice_session_id
            )
        except ValidationError as exc:
            raise NavigationSidebandError("provider_voice_session_id_invalid") from exc
        context = NavigationSidebandContext(
            voice_session_id=validated_voice_session_id,
            request_id=request_id,
        )
        monitor_url = (
            f"{PROVIDER_SIDEBAND_URL}?call_id="
            f"{quote(validated_voice_session_id, safe='')}"
        )
        try:
            websocket = await connect(
                monitor_url,
                additional_headers={
                    "Authorization": f"Bearer {settings.openai_api_key}"
                },
                open_timeout=5.0,
                max_size=MAX_PROVIDER_EVENT_BYTES,
            )
        except (OSError, TimeoutError, ValueError, WebSocketException) as exc:
            raise NavigationSidebandError("provider_sideband_unavailable") from exc
        task = asyncio.create_task(
            self._monitor(
                websocket=websocket,
                context=context,
                sender=NavigationAttestationClient(config),
            ),
            name=f"liquisto-navigation-sideband:{validated_voice_session_id}",
        )
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    async def _monitor(
        self,
        *,
        websocket: ClientConnection,
        context: NavigationSidebandContext,
        sender: AttestationSender,
    ) -> None:
        try:
            async for raw_event in websocket:
                try:
                    attestation = build_runtime_attestation(
                        raw_event=raw_event,
                        context=context,
                    )
                    if attestation is None:
                        continue
                    await sender.deliver(attestation)
                except NavigationAttestationDeliveryError as exc:
                    log.error(
                        "liquisto_assistant.navigation_attestation_failed",
                        reason=str(exc),
                        attempt_count=exc.attempt_count,
                        retry_count=exc.retry_count,
                        http_status=exc.http_status,
                        exception_class=exc.exception_class,
                        voice_session_id=context.voice_session_id,
                        request_id=context.request_id,
                        raw_audio_stored=False,
                    )
                except NavigationSidebandError as exc:
                    log.warning(
                        "liquisto_assistant.navigation_sideband_denied",
                        reason=str(exc),
                        voice_session_id=context.voice_session_id,
                        request_id=context.request_id,
                        raw_audio_stored=False,
                    )
        except (OSError, WebSocketException) as exc:
            log.warning(
                "liquisto_assistant.navigation_sideband_closed",
                reason=type(exc).__name__,
                voice_session_id=context.voice_session_id,
                request_id=context.request_id,
                raw_audio_stored=False,
            )
        finally:
            await websocket.close()

    async def close(self) -> None:
        tasks = tuple(self._tasks)
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)


navigation_sideband_manager = LiquistoNavigationSidebandManager()
