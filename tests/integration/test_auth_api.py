from __future__ import annotations

from uuid import uuid4


def _unique_email() -> str:
    return f"pytest-{uuid4().hex}@example.com"


def _register_payload(email: str, **overrides) -> dict:
    payload = {
        "first_name": "Ana",
        "last_name": "García",
        "birth_date": "1990-05-20",
        "phone": "+34 600 123 456",
        "email": email,
        "password": "supersecret123",
        "accepts_terms": True,
    }
    payload.update(overrides)
    return payload


def test_register_creates_account_and_returns_a_usable_token(client) -> None:
    email = _unique_email()
    response = client.post("/api/v1/auth/register", json=_register_payload(email))
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["user"]["email"] == email
    assert body["user"]["first_name"] == "Ana"
    assert body["user"]["last_name"] == "García"

    history = client.get("/api/v1/history", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert history.status_code == 200
    assert history.json()["items"] == []


def test_register_rejects_duplicate_email(client) -> None:
    email = _unique_email()
    client.post("/api/v1/auth/register", json=_register_payload(email))
    response = client.post("/api/v1/auth/register", json=_register_payload(email, password="otherpassword"))
    assert response.status_code == 409
    assert response.json()["error"] == "EMAIL_ALREADY_REGISTERED"


def test_register_rejects_short_password(client) -> None:
    response = client.post("/api/v1/auth/register", json=_register_payload(_unique_email(), password="short"))
    assert response.status_code == 422


def test_register_rejects_invalid_email_format(client) -> None:
    response = client.post("/api/v1/auth/register", json=_register_payload("not-an-email"))
    assert response.status_code == 422


def test_register_rejects_underage_birth_date(client) -> None:
    response = client.post("/api/v1/auth/register", json=_register_payload(_unique_email(), birth_date="2015-01-01"))
    assert response.status_code == 422


def test_register_rejects_missing_terms_acceptance(client) -> None:
    response = client.post("/api/v1/auth/register", json=_register_payload(_unique_email(), accepts_terms=False))
    assert response.status_code == 422


def test_login_succeeds_with_correct_credentials(client) -> None:
    email = _unique_email()
    client.post("/api/v1/auth/register", json=_register_payload(email))
    response = client.post("/api/v1/auth/login", json={"email": email, "password": "supersecret123"})
    assert response.status_code == 200
    assert response.json()["access_token"]


def test_login_rejects_wrong_password(client) -> None:
    email = _unique_email()
    client.post("/api/v1/auth/register", json=_register_payload(email))
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
    token_a = client.post("/api/v1/auth/register", json=_register_payload(email_a)).json()["access_token"]
    token_b = client.post("/api/v1/auth/register", json=_register_payload(email_b)).json()["access_token"]

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
