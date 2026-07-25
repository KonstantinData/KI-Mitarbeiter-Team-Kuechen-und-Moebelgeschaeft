"""Security tests for provider-attested Liquisto navigation v1.2."""

from __future__ import annotations

import json

import pytest

from src.agents.liquisto_assistant.navigation import (
    LiquistoNavigationRuntimeAttestation,
)
from src.api.config import Settings
from src.api.services import liquisto_navigation_sideband as sideband
from src.api.services.liquisto_navigation_sideband import (
    ATTESTATION_PATH,
    NavigationAttestationClient,
    NavigationAttestationDeliveryError,
    NavigationSidebandConfig,
    NavigationSidebandContext,
    NavigationSidebandError,
    build_runtime_attestation,
    validate_attestation_url,
)

RUNTIME_TOKEN = "runtime-navigation-token-32-bytes-minimum"
LOOPBACK_URL = f"http://127.0.0.1:3088{ATTESTATION_PATH}"


def tool_arguments(**changes) -> dict:
    payload = {
        "contract_version": "1.2",
        "request_id": "req-voice-123",
        "tenant_id": "liquisto",
        "agent_id": "liquisto-assistant",
        "source": "voice",
        "intent": "navigate",
        "destination_id": "crm.tasks",
        "parameters": {},
    }
    payload.update(changes)
    return payload


def provider_event(*, arguments: dict | None = None, **changes) -> str:
    payload = {
        "event_id": "event-provider-123",
        "type": "response.function_call_arguments.done",
        "name": "open_liquisto_destination",
        "call_id": "call-provider-123",
        "arguments": json.dumps(arguments or tool_arguments()),
        "item_id": "item-provider-123",
        "response_id": "response-provider-123",
        "output_index": 0,
    }
    payload.update(changes)
    return json.dumps(payload)


def context() -> NavigationSidebandContext:
    return NavigationSidebandContext(
        voice_session_id="rtc_liquisto_123",
        request_id="req-voice-123",
    )


def attestation() -> LiquistoNavigationRuntimeAttestation:
    result = build_runtime_attestation(raw_event=provider_event(), context=context())
    assert result is not None
    return result


def decision_payload() -> dict:
    return {
        "contract_version": "1.2",
        "request_id": "req-voice-123",
        "call_id": "call-provider-123",
        "decision_id": "decision-123",
        "tenant_id": "liquisto",
        "agent_id": "liquisto-assistant",
        "source": "voice",
        "intent": "navigate",
        "status": "allow",
        "destination_id": "crm.tasks",
        "parameters": {},
        "reason_code": "allowed",
        "decision_time": "2026-07-24T09:00:00.447Z",
        "message": "Navigation freigegeben: Aktuelle Aufgaben.",
    }


def test_runtime_attestation_is_exactly_derived_from_provider_event():
    result = attestation()

    assert result.model_dump(mode="json") == {
        "contract_version": "1.2",
        "provider_event_type": "response.function_call_arguments.done",
        "tool_name": "open_liquisto_destination",
        "voice_session_id": "rtc_liquisto_123",
        "call_id": "call-provider-123",
        "request_id": "req-voice-123",
        "tenant_id": "liquisto",
        "agent_id": "liquisto-assistant",
        "source": "voice",
        "intent": "navigate",
        "destination_id": "crm.tasks",
        "parameters": {},
    }


@pytest.mark.parametrize(
    "arguments",
    [
        tool_arguments(call_id="browser-selected"),
        tool_arguments(principal_id="browser-selected"),
        tool_arguments(url="https://example.invalid"),
        tool_arguments(tenant_id="mein-kuechenexperte"),
        tool_arguments(agent_id="lisa"),
        tool_arguments(destination_id="admin.users"),
        tool_arguments(parameters={"path": "/crm/tasks"}),
    ],
)
def test_provider_event_rejects_model_or_browser_authority_injection(arguments):
    with pytest.raises(
        NavigationSidebandError, match="provider_navigation_event_invalid"
    ):
        build_runtime_attestation(
            raw_event=provider_event(arguments=arguments),
            context=context(),
        )


def test_provider_event_rejects_request_correlation_mismatch():
    with pytest.raises(
        NavigationSidebandError, match="provider_navigation_request_mismatch"
    ):
        build_runtime_attestation(
            raw_event=provider_event(arguments=tool_arguments(request_id="req-other")),
            context=context(),
        )


def test_provider_event_accepts_only_done_event_and_exact_tool():
    assert (
        build_runtime_attestation(
            raw_event=provider_event(type="response.audio.done"),
            context=context(),
        )
        is None
    )
    with pytest.raises(
        NavigationSidebandError, match="provider_navigation_tool_denied"
    ):
        build_runtime_attestation(
            raw_event=provider_event(name="open_url"),
            context=context(),
        )


@pytest.mark.parametrize(
    "raw_event",
    [
        "not-json",
        "[]",
        b"\xff",
        "x" * (sideband.MAX_PROVIDER_EVENT_BYTES + 1),
    ],
    ids=["not-json", "array", "invalid-utf8", "oversized"],
)
def test_provider_event_rejects_structurally_unreadable_or_oversized_input(raw_event):
    with pytest.raises(NavigationSidebandError):
        build_runtime_attestation(raw_event=raw_event, context=context())


def test_attestation_url_is_fixed_in_production_and_loopback_only_in_tests():
    assert (
        validate_attestation_url(sideband.PRODUCTION_ATTESTATION_URL, app_env="production")
        == sideband.PRODUCTION_ATTESTATION_URL
    )
    assert validate_attestation_url(LOOPBACK_URL, app_env="test") == LOOPBACK_URL


def test_settings_reject_voice_enablement_without_sideband_kill_switch():
    with pytest.raises(
        ValueError, match="LIQUISTO_NAVIGATION_SIDEBAND_ENABLED=true"
    ):
        Settings(
            openai_api_key="provider-key-server-only",
            liquisto_assistant_voice_enabled=True,
            liquisto_navigation_sideband_enabled=False,
        )


@pytest.mark.parametrize(
    ("raw_url", "app_env"),
    [
        ("", "production"),
        (f"https://liquisto-crm-service:8080{ATTESTATION_PATH}", "production"),
        (f"http://other-service:8080{ATTESTATION_PATH}", "production"),
        (f"http://liquisto-crm-service:8080{ATTESTATION_PATH}?next=http://evil", "production"),
        ("http://127.0.0.1:3088/other", "test"),
        (f"http://foreign-service:3088{ATTESTATION_PATH}", "test"),
    ],
)
def test_attestation_url_rejects_free_urls_redirect_targets_and_foreign_hosts(
    raw_url, app_env
):
    with pytest.raises(NavigationSidebandError):
        validate_attestation_url(raw_url, app_env=app_env)


@pytest.mark.parametrize(
    "token",
    ["", "short", "x" * 31, "x" * 31 + " "],
)
def test_sideband_config_rejects_missing_short_or_whitespace_token(token):
    settings = Settings(
        app_env="test",
        liquisto_navigation_sideband_enabled=True,
        liquisto_olivia_navigation_attestation_url=LOOPBACK_URL,
        liquisto_olivia_navigation_runtime_token=token,
    )

    with pytest.raises(NavigationSidebandError, match="navigation_runtime_token_invalid"):
        NavigationSidebandConfig.from_settings(settings)


@pytest.mark.parametrize("shared_setting", ["service", "provider"])
def test_sideband_config_rejects_runtime_token_reused_for_other_authority(
    shared_setting,
):
    values = {
        "app_env": "test",
        "liquisto_navigation_sideband_enabled": True,
        "liquisto_olivia_navigation_attestation_url": LOOPBACK_URL,
        "liquisto_olivia_navigation_runtime_token": RUNTIME_TOKEN,
        "liquisto_assistant_service_token": "assistant-service-token-distinct",
        "openai_api_key": "provider-key-distinct",
    }
    values[
        "liquisto_assistant_service_token"
        if shared_setting == "service"
        else "openai_api_key"
    ] = RUNTIME_TOKEN
    settings = Settings(**values)

    with pytest.raises(
        NavigationSidebandError, match="navigation_runtime_token_not_dedicated"
    ):
        NavigationSidebandConfig.from_settings(settings)


@pytest.mark.asyncio
async def test_attestation_client_uses_dedicated_bearer_and_rejects_redirects(monkeypatch):
    calls: list[dict] = []

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return decision_payload()

    class FakeClient:
        def __init__(self, *, timeout, follow_redirects):
            assert timeout == 5.0
            assert follow_redirects is False

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, url, *, headers, json):
            calls.append({"url": url, "headers": headers, "json": json})
            return FakeResponse()

    monkeypatch.setattr(sideband.httpx, "AsyncClient", FakeClient)
    config = NavigationSidebandConfig(
        attestation_url=LOOPBACK_URL,
        runtime_token=RUNTIME_TOKEN,
        delivery_timeout_seconds=5.0,
    )

    decision = await NavigationAttestationClient(config).deliver(attestation())

    assert decision.decision_id == "decision-123"
    assert decision.model_dump(mode="json") == decision_payload()
    assert calls == [
        {
            "url": LOOPBACK_URL,
            "headers": {
                "Authorization": f"Bearer {RUNTIME_TOKEN}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            "json": attestation().model_dump(mode="json"),
        }
    ]
    assert "principal_id" not in calls[0]["json"]
    assert "attestation_id" not in calls[0]["json"]


@pytest.mark.asyncio
async def test_attestation_client_rejects_noncanonical_or_mismatched_decision(
    monkeypatch,
):
    attempts = 0

    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                **decision_payload(),
                "call_id": "call-from-another-event",
            }

    class FakeClient:
        def __init__(self, **_kwargs):
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def post(self, _url, **_kwargs):
            nonlocal attempts
            attempts += 1
            return FakeResponse()

    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr(sideband.httpx, "AsyncClient", FakeClient)
    monkeypatch.setattr(sideband.asyncio, "sleep", no_sleep)
    config = NavigationSidebandConfig(
        attestation_url=LOOPBACK_URL,
        runtime_token=RUNTIME_TOKEN,
        delivery_timeout_seconds=5.0,
    )

    with pytest.raises(
        NavigationAttestationDeliveryError,
        match="navigation_attestation_delivery_failed",
    ):
        await NavigationAttestationClient(config).deliver(attestation())

    assert attempts == 3


@pytest.mark.asyncio
async def test_sideband_manager_authenticates_provider_monitor_and_rejects_bad_rtc_id(
    monkeypatch,
):
    connect_calls: list[dict] = []

    class EmptyWebSocket:
        def __aiter__(self):
            return self

        async def __anext__(self):
            raise StopAsyncIteration

        async def close(self):
            return None

    async def fake_connect(url, **kwargs):
        connect_calls.append({"url": url, **kwargs})
        return EmptyWebSocket()

    monkeypatch.setattr(sideband, "connect", fake_connect)
    settings = Settings(
        app_env="test",
        openai_api_key="provider-key-server-only",
        liquisto_navigation_sideband_enabled=True,
        liquisto_olivia_navigation_attestation_url=LOOPBACK_URL,
        liquisto_olivia_navigation_runtime_token=RUNTIME_TOKEN,
    )
    manager = sideband.LiquistoNavigationSidebandManager()

    await manager.start(
        settings=settings,
        voice_session_id="rtc_liquisto_123",
        request_id="req-voice-123",
    )
    await manager.close()

    assert connect_calls[0]["url"] == (
        "wss://api.openai.com/v1/realtime?call_id=rtc_liquisto_123"
    )
    assert connect_calls[0]["additional_headers"] == {
        "Authorization": "Bearer provider-key-server-only"
    }
    with pytest.raises(
        NavigationSidebandError, match="provider_voice_session_id_invalid"
    ):
        await manager.start(
            settings=settings,
            voice_session_id="browser-selected",
            request_id="req-voice-123",
        )


@pytest.mark.asyncio
async def test_sideband_disconnect_after_attach_creates_no_attestation_or_decision():
    delivered_attestations: list[LiquistoNavigationRuntimeAttestation] = []

    class DroppedWebSocket:
        closed = False
        events = iter(
            [
                json.dumps(
                    {
                        "event_id": "event-provider-audio",
                        "type": "response.audio.done",
                    }
                )
            ]
        )

        def __aiter__(self):
            return self

        async def __anext__(self):
            try:
                return next(self.events)
            except StopIteration as exc:
                raise OSError("provider sideband disconnected") from exc

        async def close(self):
            self.closed = True

    class RecordingSender:
        async def deliver(self, attestation):
            delivered_attestations.append(attestation)
            return decision_payload()

    websocket = DroppedWebSocket()
    manager = sideband.LiquistoNavigationSidebandManager()

    await manager._monitor(
        websocket=websocket,
        context=context(),
        sender=RecordingSender(),
    )

    assert delivered_attestations == []
    assert websocket.closed is True
