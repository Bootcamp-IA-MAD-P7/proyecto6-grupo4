from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data.laliga_loader import build_canonical_dataset
from src.evaluation.splits import (
    FROZEN_SEASON_SPLIT,
    SPLIT_SEED,
    TEST_SEASONS,
    TRAIN_SEASONS,
    VALIDATION_SEASONS,
    assign_splits,
    build_split_manifest,
    freeze_splits,
)


def _seasoned_frame(seasons: list[str]) -> pd.DataFrame:
    return pd.DataFrame({"season": seasons})


def test_season_partition_is_disjoint_and_covers_all_frozen_seasons() -> None:
    train = set(TRAIN_SEASONS)
    validation = set(VALIDATION_SEASONS)
    test = set(TEST_SEASONS)

    assert train & validation == set()
    assert train & test == set()
    assert validation & test == set()
    assert set(FROZEN_SEASON_SPLIT) == train | validation | test


def test_test_seasons_are_strictly_after_validation_and_train() -> None:
    assert max(TRAIN_SEASONS) < min(VALIDATION_SEASONS)
    assert max(VALIDATION_SEASONS) < min(TEST_SEASONS)


def test_assign_splits_maps_known_seasons() -> None:
    frame = _seasoned_frame([TRAIN_SEASONS[0], VALIDATION_SEASONS[0], TEST_SEASONS[-1]])

    result = assign_splits(frame)

    assert list(result) == ["train", "validation", "test"]


def test_assign_splits_rejects_unknown_season() -> None:
    frame = _seasoned_frame(["2099-00"])

    with pytest.raises(ValueError, match="no contempladas"):
        assign_splits(frame)


def test_freeze_splits_writes_reproducible_outputs(tmp_path: Path) -> None:
    historical = pd.DataFrame(
        [
            ["1995-96", "02-09-1995", "Alpha", "Beta", 2, 1, "H", 1, 0, "H"],
            ["2021-22", "10-09-2021", "Gamma", "Delta", 0, 0, "D", 0, 0, "D"],
            ["2025-26", "15-08-2025", "Epsilon", "Zeta", 1, 2, "A", 0, 1, "A"],
        ],
        columns=["Season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR"],
    )
    empty_detailed_columns = [
        "Div", "Date", "Time", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
        "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR",
        "AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5", "AHh", "AvgAHH", "AvgAHA",
        "AvgCH", "AvgCD", "AvgCA", "AvgC>2.5", "AvgC<2.5", "AHCh", "AvgCAHH", "AvgCAHA",
    ]
    detailed = pd.DataFrame(columns=empty_detailed_columns)
    canonical = build_canonical_dataset(historical, detailed)
    processed_path = tmp_path / "clean.csv"
    canonical.to_csv(processed_path, index=False, date_format="%Y-%m-%d")

    splits_path = tmp_path / "splits" / "laliga_splits.csv"
    manifest_path = tmp_path / "split_manifest.json"

    manifest = freeze_splits(processed_path, splits_path, manifest_path)

    assert splits_path.exists()
    output = pd.read_csv(splits_path)
    assert set(output.columns) == {"match_id", "season", "split"}
    assert dict(zip(output["season"], output["split"])) == {
        "1995-96": "train",
        "2021-22": "validation",
        "2025-26": "test",
    }
    assert manifest["seed"] == SPLIT_SEED
    assert manifest["status"] == "frozen_i1_approved_pending_i3_i4_cross_review"
    assert manifest["technical_approvals"]["I1"]["status"] == "approved"
    assert manifest["required_cross_reviewers_pending"] == ["I3", "I4"]
    assert manifest["row_counts"] == {"train": 1, "validation": 1, "test": 1}
    assert manifest["source_dataset"]["rows"] == 3
