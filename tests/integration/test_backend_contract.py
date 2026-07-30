from __future__ import annotations

import subprocess
import sys
from pathlib import Path

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


def test_predictions_endpoint_requires_authentication() -> None:
    client = TestClient(app)
    response = client.post(
        "/api/v1/predictions",
        json={"home_team": "Real Madrid", "away_team": "Barcelona", "match_date": "2026-10-25"},
    )
    assert response.status_code == 401
    assert response.json()["error"] == "UNAUTHORIZED"


def test_predictions_endpoint_returns_404_for_unknown_team(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/predictions",
        json={"home_team": "Equipo Inexistente FC", "away_team": "Barcelona", "match_date": "2026-10-25"},
        headers=auth_headers,
    )
    assert response.status_code == 404
    assert response.json()["error"] == "TEAM_NOT_FOUND"


def test_predictions_endpoint_returns_409_for_insufficient_history(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/predictions",
        json={"home_team": "Real Madrid", "away_team": "Barcelona", "match_date": "1990-01-01"},
        headers=auth_headers,
    )
    assert response.status_code == 409
    assert response.json()["error"] == "INSUFFICIENT_HISTORY"


def test_predictions_endpoint_rejects_payloads_over_4kib(client, auth_headers) -> None:
    oversized_comment = "x" * 5000
    response = client.post(
        "/api/v1/predictions",
        content=(
            '{"home_team":"Real Madrid","away_team":"Barcelona","match_date":"2026-10-25","padding":"'
            + oversized_comment
            + '"}'
        ),
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json()["error"] == "PAYLOAD_TOO_LARGE"


def test_predictions_endpoint_returns_400_for_malformed_json(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/predictions",
        content="{esto no es json valido",
        headers={**auth_headers, "Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["error"] == "MALFORMED_JSON"


def test_module_import_configures_logging_so_info_level_actually_prints() -> None:
    # Regresion real: logger.info() sin logging.basicConfig() queda
    # silenciado por el "handler of last resort" de Python (solo WARNING+),
    # asi que el log estructurado exigido por RNF-06 nunca aparecia en un
    # proceso real (uvicorn/Docker). pytest's caplog NO detecta este bug
    # porque instala su propio handler en el root logger independientemente
    # de que basicConfig se haya llamado o no; por eso esta prueba lanza un
    # proceso Python nuevo, igual que correria uvicorn en produccion.
    probe = (
        "import app.backend.main\n"
        "import logging\n"
        "logging.getLogger('laliga.backend').info('request_id=probe123 method=GET path=/probe status=200')\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=str(Path(__file__).resolve().parents[2]),
        capture_output=True, text=True, timeout=60,
    )
    combined = result.stdout + result.stderr
    assert "request_id=probe123" in combined, f"log no emitido en un proceso real; salida={combined!r}"


def test_predictions_response_request_id_matches_error_envelope_shape(client, auth_headers) -> None:
    response = client.post(
        "/api/v1/predictions",
        json={"home_team": "Real Madrid", "away_team": "Barcelona", "match_date": "2026-10-25"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    body = response.json()
    assert body["request_id"]
    # El mismo request_id que se devuelve al cliente es el que se usaria en el log
    # estructurado de esa peticion (misma fuente: request.state.request_id).
