from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from src.data.historical_features import FEATURE_GENERATOR_VERSION, generate_historical_features
from src.data.laliga_loader import file_sha256, load_processed_dataset


def test_historical_feature_generation_is_reproducible_against_frozen_splits(tmp_path: Path) -> None:
    processed_path = Path("data/processed/laliga_matches_clean.csv")
    splits_path = Path("data/processed/splits/laliga_splits.csv")
    first_output, first_manifest = generate_historical_features(
        processed_path,
        splits_path,
        tmp_path / "first.csv",
        tmp_path / "first_manifest.json",
    )
    second_output, second_manifest = generate_historical_features(
        processed_path,
        splits_path,
        tmp_path / "second.csv",
        tmp_path / "second_manifest.json",
    )

    source = load_processed_dataset(processed_path)
    frozen_splits = pd.read_csv(splits_path)
    assert first_manifest["feature_generator_version"] == FEATURE_GENERATOR_VERSION
    assert first_manifest["source_dataset"]["sha256"] == file_sha256(processed_path)
    assert first_manifest["source_dataset"]["rows"] == len(source)
    assert first_manifest["split_counts"] == frozen_splits["split"].value_counts().sort_index().to_dict()
    assert set(first_output["match_id"]) == set(source["match_id"])
    assert first_output["match_id"].is_unique
    pd.testing.assert_frame_equal(first_output, second_output)
    assert first_manifest["schema"] == second_manifest["schema"]
    assert file_sha256(tmp_path / "first.csv") == file_sha256(tmp_path / "second.csv")
    assert json.loads((tmp_path / "first_manifest.json").read_text(encoding="utf-8"))["features_output"]["rows"] == len(source)
