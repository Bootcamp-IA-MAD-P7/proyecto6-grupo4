from __future__ import annotations

import pandas as pd
import pytest

from src.candidates.common import load_training_partitions, upsert_experiment
from src.data.historical_features import MODEL_FEATURES
from src.data.laliga_loader import TARGET_COLUMN


def _valid_features_csv(tmp_path):
    rows = 12
    frame = pd.DataFrame({
        "match_id": [f"m{i}" for i in range(rows)],
        "split": ["train"] * 8 + ["validation"] * 4,
        "home_team": ["A", "B", "C"] * 4,
        "away_team": ["B", "C", "A"] * 4,
        TARGET_COLUMN: ["H", "D", "A"] * 4,
        **{column: [float(i) for i in range(rows)] for column in MODEL_FEATURES[2:]},
    })
    path = tmp_path / "features.csv"
    frame.to_csv(path, index=False)
    return path


def test_load_training_partitions_splits_train_and_validation(tmp_path) -> None:
    path = _valid_features_csv(tmp_path)
    train, validation = load_training_partitions(path)
    assert len(train) == 8
    assert len(validation) == 4
    assert set(train["split"]) == {"train"}
    assert set(validation["split"]) == {"validation"}


def test_load_training_partitions_rejects_missing_required_columns(tmp_path) -> None:
    path = tmp_path / "bad.csv"
    pd.DataFrame({"match_id": ["m1"], "split": ["train"]}).to_csv(path, index=False)
    with pytest.raises(ValueError):
        load_training_partitions(path)


def test_load_training_partitions_rejects_duplicate_match_ids(tmp_path) -> None:
    rows = 6
    frame = pd.DataFrame({
        "match_id": ["m0"] * rows,
        "split": ["train"] * 4 + ["validation"] * 2,
        "home_team": ["A", "B", "C"] * 2,
        "away_team": ["B", "C", "A"] * 2,
        TARGET_COLUMN: ["H", "D", "A"] * 2,
        **{column: [float(i) for i in range(rows)] for column in MODEL_FEATURES[2:]},
    })
    path = tmp_path / "duplicate.csv"
    frame.to_csv(path, index=False)
    with pytest.raises(ValueError):
        load_training_partitions(path)


def test_upsert_experiment_rejects_schema_drift(tmp_path) -> None:
    path = tmp_path / "table.csv"
    pd.DataFrame([{"candidate_id": "A", "status": "ready_for_comparison"}]).to_csv(path, index=False)
    with pytest.raises(ValueError, match="contrato de la tabla"):
        upsert_experiment(path, {"candidate_id": "A", "status": "ready_for_comparison", "extra_unexpected_field": "x"})


def test_upsert_experiment_updates_existing_row_in_place(tmp_path) -> None:
    path = tmp_path / "table.csv"
    pd.DataFrame([
        {"candidate_id": "A", "status": "pending"},
        {"candidate_id": "B", "status": "pending"},
    ]).to_csv(path, index=False)
    upsert_experiment(path, {"candidate_id": "A", "status": "ready_for_comparison"})
    result = pd.read_csv(path)
    assert len(result) == 2  # no se duplica la fila
    assert result.loc[result["candidate_id"].eq("A"), "status"].iloc[0] == "ready_for_comparison"
    assert result.loc[result["candidate_id"].eq("B"), "status"].iloc[0] == "pending"
