from __future__ import annotations

import pandas as pd

from src.data.laliga_loader import audit_dataset, build_canonical_dataset


def _historical() -> pd.DataFrame:
    return pd.DataFrame(
        [
            ["2024-25", "18-05-2025", "Alpha", "Beta", 2, 1, "H", 1, 0, "H"],
            ["2025-26", "15-08-2025", "Gamma", "Delta", 1, 1, "D", 0, 1, "A"],
        ],
        columns=["Season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR"],
    )


def _detailed() -> pd.DataFrame:
    row = {
        "Div": "SP1", "Date": "2025-08-15", "Time": "20:30", "HomeTeam": "Gamma", "AwayTeam": "Delta",
        "FTHG": 1, "FTAG": 1, "FTR": "D", "HTHG": 0, "HTAG": 1, "HTR": "A",
        "HS": 10, "AS": 8, "HST": 4, "AST": 3, "HF": 12, "AF": 11, "HC": 5, "AC": 4,
        "HY": 2, "AY": 3, "HR": 0, "AR": 0, "AvgH": 2.0, "AvgD": 3.2, "AvgA": 3.8,
        "Avg>2.5": 1.9, "Avg<2.5": 1.9, "AHh": -0.25, "AvgAHH": 1.9, "AvgAHA": 1.95,
        "AvgCH": 2.1, "AvgCD": 3.1, "AvgCA": 3.7, "AvgC>2.5": 1.95, "AvgC<2.5": 1.85,
        "AHCh": -0.25, "AvgCAHH": 1.92, "AvgCAHA": 1.93,
    }
    return pd.DataFrame([row])


def test_build_canonical_dataset_deduplicates_and_prioritizes_detail() -> None:
    result = build_canonical_dataset(_historical(), _detailed())

    assert len(result) == 2
    assert result["match_id"].is_unique
    detailed_row = result.loc[result["home_team"].eq("Gamma")].iloc[0]
    assert detailed_row["source_coverage"] == "both_sources"
    assert bool(detailed_row["has_detailed_stats"])
    assert detailed_row["shots_home"] == 10


def test_derived_fields_and_season_are_consistent() -> None:
    result = build_canonical_dataset(_historical(), _detailed())
    row = result.loc[result["home_team"].eq("Alpha")].iloc[0]

    assert row["season"] == "2024-25"
    assert row["total_goals"] == 3
    assert row["goal_diff_home"] == 1
    assert row["home_points"] == 3
    assert bool(row["both_teams_scored"])


def test_audit_rejects_no_valid_rows() -> None:
    audit = audit_dataset(build_canonical_dataset(_historical(), _detailed()))

    assert audit["duplicate_match_ids"] == 0
    assert audit["full_time_result_inconsistencies"] == 0
    assert audit["missing_target"] == 0
