from __future__ import annotations

import json
from pathlib import Path

from src.data.laliga_eda import run_full_eda
from src.data.laliga_loader import build_canonical_dataset
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
