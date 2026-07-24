from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data.laliga_eda import run_full_eda
from src.data.laliga_loader import DETAILED_SOURCE_COLUMNS, build_canonical_dataset
from tests.unit.test_laliga_loader import _detailed, _historical


def test_full_eda_writes_reproducible_artifacts(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    frame = build_canonical_dataset(_historical(), _detailed())

    metrics = run_full_eda(frame, reports)

    assert metrics["quality"]["rows"] == 2
    assert (reports / "laliga_eda.md").exists()
    assert (reports / "metrics/data_dictionary.csv").exists()
    assert len(list((reports / "figures").glob("*.png"))) == 11
    persisted = json.loads((reports / "metrics/eda_summary.json").read_text(encoding="utf-8"))
    assert persisted["quality"]["duplicate_match_ids"] == 0
    report = (reports / "laliga_eda.md").read_text(encoding="utf-8")
    assert "conjunto de desarrollo (train + validation)" in report
    assert "Los splits ya están congelados" in report
    assert "En 2025-26, tiros" not in report
    assert "no se han creado splits" not in report


def test_full_eda_handles_development_data_without_market_rows(tmp_path: Path) -> None:
    reports = tmp_path / "reports"
    frame = build_canonical_dataset(_historical(), pd.DataFrame(columns=DETAILED_SOURCE_COLUMNS))

    metrics = run_full_eda(frame, reports)

    assert metrics["market_baseline"]["status"] == "not_available_without_development_opening_odds"
    assert metrics["market_baseline"]["rows_with_complete_opening_odds"] == 0
    assert len(list((reports / "figures").glob("*.png"))) == 11
