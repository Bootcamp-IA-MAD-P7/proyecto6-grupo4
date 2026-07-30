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
    response = client.post(
        "/api/v1/auth/register",
        json={
            "first_name": "Ana",
            "last_name": "García",
            "birth_date": "1990-05-20",
            "phone": "+34 600 123 456",
            "email": email,
            "password": "supersecret123",
            "accepts_terms": True,
        },
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
