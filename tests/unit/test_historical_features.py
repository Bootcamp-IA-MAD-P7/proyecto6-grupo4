from __future__ import annotations

import pandas as pd
import pytest

from src.data.historical_features import (
    MODEL_FEATURES,
    HistoricalFeatureConfig,
    build_historical_features,
)


def _matches() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ("m1", "2020-21", "2020-01-01", "Alpha", "Beta", 2, 1, "H"),
            ("m2", "2020-21", "2020-01-08", "Alpha", "Gamma", 0, 0, "D"),
            ("m3", "2020-21", "2020-01-08", "Beta", "Delta", 1, 0, "H"),
            ("m4", "2020-21", "2020-01-15", "Gamma", "Alpha", 1, 3, "A"),
        ],
        columns=[
            "match_id", "season", "match_date", "home_team", "away_team",
            "home_goals_ft", "away_goals_ft", "result_ft",
        ],
    )


def test_first_match_has_only_cold_start_history() -> None:
    result = build_historical_features(_matches())
    first = result.iloc[0]

    assert first["home_matches_played"] == 0
    assert first["away_matches_played"] == 0
    assert first["home_points_per_match_5"] == 0
    assert first["home_elo_pre_match"] == 1500
    assert first["home_days_since_last_match"] == -1


def test_previous_match_is_used_but_current_match_is_not() -> None:
    result = build_historical_features(_matches())
    alpha_second = result.loc[result["match_id"].eq("m2")].iloc[0]

    assert alpha_second["home_matches_played"] == 1
    assert alpha_second["home_points_per_match_5"] == 3
    assert alpha_second["home_goals_for_per_match_5"] == 2
    assert alpha_second["home_goals_against_per_match_5"] == 1
    assert alpha_second["home_win_rate_5"] == 1
    assert alpha_second["home_days_since_last_match"] == 7


def test_matches_on_same_date_share_the_pre_date_snapshot() -> None:
    same_day = pd.DataFrame(
        [
            ("m1", "2020-21", "2020-01-01", "Alpha", "Beta", 2, 0, "H"),
            ("m2", "2020-21", "2020-01-08", "Alpha", "Gamma", 1, 0, "H"),
            ("m3", "2020-21", "2020-01-08", "Alpha", "Delta", 0, 1, "A"),
        ],
        columns=_matches().columns,
    )
    result = build_historical_features(same_day)
    alpha_same_day = result.loc[result["match_id"].isin(["m2", "m3"])]

    assert alpha_same_day["home_matches_played"].tolist() == [1.0, 1.0]
    assert alpha_same_day["home_points_per_match_5"].tolist() == [3.0, 3.0]
    assert alpha_same_day["home_elo_pre_match"].nunique() == 1


def test_future_result_cannot_change_features_of_earlier_matches() -> None:
    original = _matches()
    altered = original.copy()
    altered.loc[altered["match_id"].eq("m4"), ["home_goals_ft", "away_goals_ft", "result_ft"]] = [4, 0, "H"]

    baseline = build_historical_features(original)
    changed = build_historical_features(altered)

    earlier = baseline["match_id"].isin(["m1", "m2", "m3"])
    pd.testing.assert_frame_equal(
        baseline.loc[earlier, list(MODEL_FEATURES)].reset_index(drop=True),
        changed.loc[earlier, list(MODEL_FEATURES)].reset_index(drop=True),
    )


def test_output_is_deterministic_and_uses_stable_chronological_order() -> None:
    shuffled = _matches().sample(frac=1, random_state=42)

    ordered_result = build_historical_features(_matches(), HistoricalFeatureConfig())
    shuffled_result = build_historical_features(shuffled, HistoricalFeatureConfig())

    pd.testing.assert_frame_equal(ordered_result, shuffled_result)


def test_rejects_invalid_generator_parameters() -> None:
    with pytest.raises(ValueError, match="rolling_window"):
        build_historical_features(_matches(), HistoricalFeatureConfig(rolling_window=0))
