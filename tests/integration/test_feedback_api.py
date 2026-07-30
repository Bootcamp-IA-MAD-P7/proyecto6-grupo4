from __future__ import annotations

from fastapi.testclient import TestClient

import app.backend.main as backend_main
from app.backend.main import app
from src.feedback.store import load_feedback


def test_feedback_endpoint_stores_valid_feedback_and_is_recoverable(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(backend_main, "FEEDBACK_PATH", tmp_path / "predictions_feedback.csv")
    client = TestClient(app)
    response = client.post(
        "/api/v1/feedback",
        json={
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "match_date": "2026-09-10",
            "actual_result": "H",
            "predicted_result": "D",
            "model_version": "ensemble_abcd_soft_voting_v1",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["feedback_id"]

    recovered = load_feedback(backend_main.FEEDBACK_PATH)
    assert len(recovered) == 1
    assert recovered[0]["feedback_id"] == body["feedback_id"]
    assert recovered[0]["actual_result"] == "H"


def test_feedback_endpoint_rejects_same_home_and_away_team(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(backend_main, "FEEDBACK_PATH", tmp_path / "predictions_feedback.csv")
    client = TestClient(app)
    response = client.post(
        "/api/v1/feedback",
        json={
            "home_team": "Barcelona",
            "away_team": "barcelona",
            "match_date": "2026-09-10",
            "actual_result": "H",
        },
    )
    assert response.status_code == 422
    assert response.json()["error"] == "INVALID_INPUT"


def test_feedback_endpoint_rejects_invalid_actual_result(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(backend_main, "FEEDBACK_PATH", tmp_path / "predictions_feedback.csv")
    client = TestClient(app)
    response = client.post(
        "/api/v1/feedback",
        json={
            "home_team": "Real Madrid",
            "away_team": "Barcelona",
            "match_date": "2026-09-10",
            "actual_result": "X",
        },
    )
    assert response.status_code == 422
