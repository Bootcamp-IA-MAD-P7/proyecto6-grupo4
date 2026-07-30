from __future__ import annotations

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.backend.main import app


@pytest.fixture()
def client():
    """TestClient con el lifespan activo: crea el esquema de la base de datos."""

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def auth_headers(client) -> dict[str, str]:
    """Registra un usuario único y devuelve el header Authorization listo para usar."""

    email = f"pytest-{uuid4().hex}@example.com"
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
