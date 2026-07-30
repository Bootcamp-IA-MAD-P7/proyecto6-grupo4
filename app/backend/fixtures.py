"""Catálogo de calendario (temporada 2026/27) para la home y la búsqueda por equipo.

Fuente: `data/fixtures/laliga_2026_27.json`, generado a partir de datos
abiertos de calendario (openfootball/espana, dominio público) enriquecidos
con estadio/ciudad por equipo. No requiere red en tiempo de ejecución.
"""
from __future__ import annotations

import json
from datetime import date, datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

FIXTURES_PATH = Path(__file__).resolve().parents[2] / "data/fixtures/laliga_2026_27.json"


@lru_cache(maxsize=1)
def load_fixtures() -> list[dict[str, Any]]:
    if not FIXTURES_PATH.exists():
        return []
    return json.loads(FIXTURES_PATH.read_text(encoding="utf-8"))


def list_teams() -> list[dict[str, str]]:
    seen: dict[str, str] = {}
    for match in load_fixtures():
        seen[match["home_team"]] = match["home_label"]
        seen[match["away_team"]] = match["away_label"]
    return [{"value": value, "label": label} for value, label in sorted(seen.items(), key=lambda item: item[1])]


def upcoming_fixtures(*, today: date, days: int = 30) -> list[dict[str, Any]]:
    end = today.toordinal() + days
    matches = [
        m for m in load_fixtures()
        if today.toordinal() <= date.fromisoformat(m["date"]).toordinal() <= end
    ]
    return sorted(matches, key=lambda m: (m["date"], m["time"]))


def fixtures_for_team(*, team: str, today: date) -> list[dict[str, Any]]:
    matches = [
        m for m in load_fixtures()
        if (m["home_team"] == team or m["away_team"] == team) and date.fromisoformat(m["date"]) >= today
    ]
    return sorted(matches, key=lambda m: (m["date"], m["time"]))
