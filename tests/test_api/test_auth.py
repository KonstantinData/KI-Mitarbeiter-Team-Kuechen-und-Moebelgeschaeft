"""Tests für den Auth-Endpoint."""

import pytest


@pytest.mark.asyncio
async def test_login_success(client):
    """POST /auth/login mit korrekten Credentials gibt Token zurück."""
    response = await client.post(
        "/auth/login",
        json={"username": "admin", "password": "secret"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    """POST /auth/login mit falschem Passwort gibt 401 zurück."""
    response = await client.post(
        "/auth/login",
        json={"username": "admin", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_user(client):
    """POST /auth/login mit unbekanntem User gibt 401 zurück."""
    response = await client.post(
        "/auth/login",
        json={"username": "unknown", "password": "secret"},
    )
    assert response.status_code == 401
