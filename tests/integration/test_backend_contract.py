from __future__ import annotations

from fastapi.testclient import TestClient

from app.backend.main import app


def test_health_endpoint_reports_ok_status() -> None:
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True
    assert response.json()["model_version"] == "ensemble_abcd_soft_voting_v1"


def test_root_serves_the_client_demo() -> None:
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    assert "LaLiga" in response.text


def test_predictions_endpoint_returns_404_for_unknown_team() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/predictions",
        json={"home_team": "Equipo Inexistente FC", "away_team": "Barcelona", "match_date": "2026-10-25"},
    )
    assert response.status_code == 404
    assert response.json()["error"] == "TEAM_NOT_FOUND"


def test_predictions_endpoint_returns_409_for_insufficient_history() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/predictions",
        json={"home_team": "Real Madrid", "away_team": "Barcelona", "match_date": "1990-01-01"},
    )
    assert response.status_code == 409
    assert response.json()["error"] == "INSUFFICIENT_HISTORY"
