from __future__ import annotations

from src.data.laliga_eda import build_data_dictionary, calculate_eda_metrics
from tests.unit.test_laliga_loader import _detailed, _historical
from src.data.laliga_loader import build_canonical_dataset


def test_data_dictionary_flags_target_identifier_and_leakage() -> None:
    frame = build_canonical_dataset(_historical(), _detailed())
    dictionary = build_data_dictionary(frame).set_index("column")

    assert dictionary.loc["result_ft", "role"] == "target"
    assert dictionary.loc["match_id", "role"] == "identifier"
    assert dictionary.loc["shots_home", "leakage_risk"] == "critical_post_event"
    assert dictionary.loc["odds_avg_home_open", "available_at_inference"] == "pre_match"
    assert dictionary.loc["odds_avg_home_close", "leakage_risk"] == "timing_risk"


def test_metrics_include_quality_target_and_market_baseline() -> None:
    metrics = calculate_eda_metrics(build_canonical_dataset(_historical(), _detailed()))

    assert metrics["quality"]["rows"] == 2
    assert sum(metrics["target"]["counts"].values()) == 2
    assert metrics["market_baseline"]["rows_with_complete_opening_odds"] == 1
