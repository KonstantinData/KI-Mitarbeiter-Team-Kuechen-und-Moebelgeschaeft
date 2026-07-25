"""
OpenAI Realtime Adapter
=======================
What:    Small adapter for OpenAI Realtime WebRTC session creation.
Does:    Sends browser SDP plus server-side session config to OpenAI and returns SDP answer data.
Why:     Keeps provider-specific Realtime details out of FastAPI routes and browser code.
Who:     Voice session routes.
Depends: httpx, src.api.config
"""

import json
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from urllib.parse import quote

import httpx

from src.api.config import Settings

PROVIDER_CALL_ID_RE = re.compile(r"^rtc_[A-Za-z0-9_-]{1,196}$")


@dataclass(frozen=True)
class RealtimeCallResult:
    """Safe connection material returned to the browser."""

    sdp_answer: str
    provider_call_id: str | None
    expires_at: datetime


class OpenAIRealtimeAdapter:
    """Creates WebRTC calls via the OpenAI Realtime unified interface."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def create_webrtc_call(
        self,
        *,
        client_sdp: str,
        session_config: dict,
        safety_identifier: str,
    ) -> RealtimeCallResult:
        """Creates a provider-side Realtime call and returns the SDP answer."""
        files = {
            "sdp": (None, client_sdp),
            "session": (None, json.dumps(session_config)),
        }
        headers = {
            "Authorization": f"Bearer {self._settings.openai_api_key}",
            "OpenAI-Safety-Identifier": safety_identifier,
        }
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/calls",
                headers=headers,
                files=files,
            )
        response.raise_for_status()

        location = response.headers.get("Location", "")
        provider_call_id = location.rstrip("/").split("/")[-1] if location else None
        if provider_call_id and not PROVIDER_CALL_ID_RE.fullmatch(provider_call_id):
            provider_call_id = None
        return RealtimeCallResult(
            sdp_answer=response.text,
            provider_call_id=provider_call_id,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=5),
        )

    async def hangup_call(self, *, provider_call_id: str) -> None:
        """Terminates a call that cannot obtain its required server-side monitor."""

        headers = {"Authorization": f"Bearer {self._settings.openai_api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://api.openai.com/v1/realtime/calls/"
                f"{quote(provider_call_id, safe='')}/hangup",
                headers=headers,
            )
        response.raise_for_status()
