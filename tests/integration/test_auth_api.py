from __future__ import annotations

from uuid import uuid4


def _unique_email() -> str:
    return f"pytest-{uuid4().hex}@example.com"


def test_register_creates_account_and_returns_a_usable_token(client) -> None:
    email = _unique_email()
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == email

    history = client.get("/api/v1/history", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert history.status_code == 200
    assert history.json()["items"] == []


def test_register_rejects_duplicate_email(client) -> None:
    email = _unique_email()
    client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    response = client.post("/api/v1/auth/register", json={"email": email, "password": "otherpassword"})
    assert response.status_code == 409
    assert response.json()["error"] == "EMAIL_ALREADY_REGISTERED"


def test_register_rejects_short_password(client) -> None:
    response = client.post("/api/v1/auth/register", json={"email": _unique_email(), "password": "short"})
    assert response.status_code == 422


def test_register_rejects_invalid_email_format(client) -> None:
    response = client.post("/api/v1/auth/register", json={"email": "not-an-email", "password": "supersecret123"})
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client) -> None:
    email = _unique_email()
    client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "supersecret123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(client) -> None:
    email = _unique_email()
    client.post("/api/v1/auth/register", json={"email": email, "password": "supersecret123"})
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "wrong-password"})
    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


def test_login_rejects_unknown_email(client) -> None:
    response = client.post("/api/v1/auth/login", json={"email": _unique_email(), "password": "whatever123"})
    assert response.status_code == 401
    assert response.json()["error"] == "INVALID_CREDENTIALS"


def test_history_requires_authentication(client) -> None:
    response = client.get("/api/v1/history")
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_history_rejects_garbage_token(client) -> None:
    response = client.get("/api/v1/history", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_history_only_returns_the_authenticated_users_own_predictions(client) -> None:
    email_a = _unique_email()
    email_b = _unique_email()
    token_a = client.post("/api/v1/auth/register", json={"email": email_a, "password": "supersecret123"}).json()["access_token"]
    token_b = client.post("/api/v1/auth/register", json={"email": email_b, "password": "supersecret123"}).json()["access_token"]

    client.post(
        "/api/v1/predictions",
        json={"home_team": "Real Madrid", "away_team": "Barcelona", "match_date": "2026-10-25"},
        headers={"Authorization": f"Bearer {token_a}"},
    )

    history_a = client.get("/api/v1/history", headers={"Authorization": f"Bearer {token_a}"})
    history_b = client.get("/api/v1/history", headers={"Authorization": f"Bearer {token_b}"})

    assert len(history_a.json()["items"]) == 1
    assert history_a.json()["items"][0]["home_team"] == "Real Madrid"
    assert history_b.json()["items"] == []
