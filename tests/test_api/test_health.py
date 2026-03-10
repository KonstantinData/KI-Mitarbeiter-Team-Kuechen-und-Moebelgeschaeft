"""Tests für den Health-Check Endpoint."""

import pytest


@pytest.mark.asyncio
async def test_health_check(client):
    """GET /health gibt 200 mit Status 'ok' zurück."""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "env" in data
