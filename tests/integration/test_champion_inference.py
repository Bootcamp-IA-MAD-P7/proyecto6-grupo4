from __future__ import annotations

from unittest.mock import patch

import pandas as pd

from src.inference.champion import ChampionPredictor


def test_inference_uses_exactly_the_training_feature_schema() -> None:
    predictor = ChampionPredictor("data/processed/laliga_matches_clean.csv", "models/champion/laliga_champion_v1.joblib", "reports/experiments/champion_metadata.json")
    features = pd.read_csv("data/processed/laliga_historical_features_v1.csv", parse_dates=["match_date"])
    reference = features.loc[features["split"].eq("validation")].iloc[0]
    inferred = predictor.feature_row(reference.home_team, reference.away_team, reference.match_date.date())
    expected = reference.loc[inferred.columns].to_frame().T
    pd.testing.assert_frame_equal(inferred.reset_index(drop=True), expected.reset_index(drop=True), check_dtype=False)


def test_prediction_api_returns_the_versioned_contract_and_controlled_errors(client, auth_headers) -> None:
    good = client.post("/api/v1/predictions", json={"home_team": "Barcelona", "away_team": "Real Madrid", "match_date": "2026-10-25"}, headers=auth_headers)
    assert good.status_code == 200
    assert good.json()["contract_version"] == "1.0"
    assert set(good.json()["probabilities"]) == {"H", "D", "A"}
    assert abs(sum(good.json()["probabilities"].values()) - 1) < 1e-6
    invalid = client.post("/api/v1/predictions", json={"home_team": "Barcelona", "away_team": "barcelona", "match_date": "2026-10-25"}, headers=auth_headers)
    assert invalid.status_code == 422
    assert invalid.json()["error"] == "INVALID_INPUT"


def test_future_inference_does_not_rebuild_the_complete_history() -> None:
    predictor = ChampionPredictor(
        "data/processed/laliga_matches_clean.csv",
        "models/champion/laliga_champion_v1.joblib",
        "reports/experiments/champion_metadata.json",
    )

    with patch(
        "src.inference.champion.build_historical_features",
        side_effect=AssertionError("No debe regenerar todo el histórico."),
    ):
        features = predictor.feature_row(
            "Real Madrid",
            "Barcelona",
            pd.Timestamp("2026-10-25").date(),
        )

    assert list(features.columns) == list(predictor.metadata["feature_columns"])
