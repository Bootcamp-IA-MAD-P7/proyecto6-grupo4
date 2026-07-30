from __future__ import annotations

import pandas as pd
import pytest

from src.data.ingestion import stage_new_matches, validate_new_matches


def _existing_processed(tmp_path):
    frame = pd.DataFrame(
        {
            "match_id": ["2026-01-10_real_madrid_barcelona"],
            "season": ["2025-26"],
            "match_date": ["2026-01-10"],
            "match_time": [""],
            "match_year": [2026],
            "match_month": [1],
            "iso_weekday": [6],
            "home_team": ["Real Madrid"],
            "away_team": ["Barcelona"],
            "home_goals_ft": [2],
            "away_goals_ft": [1],
            "result_ft": ["H"],
            "home_goals_ht": [1],
            "away_goals_ht": [0],
            "result_ht": ["H"],
            "total_goals": [3],
            "goal_diff_home": [1],
            "both_teams_scored": [True],
            "over_2_5": [True],
            "clean_sheet_home": [False],
            "clean_sheet_away": [False],
            "home_points": [3],
            "away_points": [0],
            "source_coverage": ["detailed_only"],
            "has_detailed_stats": [True],
            "league_code": ["SP1"],
        }
    )
    from src.data.laliga_loader import CANONICAL_COLUMNS

    for column in CANONICAL_COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    path = tmp_path / "existing_processed.csv"
    frame.loc[:, CANONICAL_COLUMNS].to_csv(path, index=False)
    return path


def _new_raw_row(**overrides) -> pd.DataFrame:
    row = {
        "Date": "20/01/2026",
        "HomeTeam": "Sevilla",
        "AwayTeam": "Betis",
        "FTHG": 1,
        "FTAG": 1,
        "FTR": "D",
        "HTHG": 0,
        "HTAG": 0,
        "HTR": "D",
    }
    row.update(overrides)
    return pd.DataFrame([row])


def test_validate_new_matches_accepts_a_genuinely_new_future_match(tmp_path) -> None:
    existing_path = _existing_processed(tmp_path)
    staged, report = validate_new_matches(_new_raw_row(), existing_path)
    assert report["rows_accepted_for_staging"] == 1
    assert staged.iloc[0]["home_team"] == "Sevilla"
    assert staged.iloc[0]["result_ft"] == "D"


def test_validate_new_matches_rejects_duplicate_of_existing_training_row(tmp_path) -> None:
    existing_path = _existing_processed(tmp_path)
    duplicate = _new_raw_row(Date="10/01/2026", HomeTeam="Real Madrid", AwayTeam="Barcelona", FTHG=2, FTAG=1, FTR="H")
    staged, report = validate_new_matches(duplicate, existing_path)
    assert report["rows_accepted_for_staging"] == 0
    assert report["rows_rejected_as_duplicates_of_training_data"] == 1
    assert staged.empty


def test_validate_new_matches_rejects_rows_not_newer_than_training_data(tmp_path) -> None:
    existing_path = _existing_processed(tmp_path)
    old_match = _new_raw_row(Date="01/01/2020", HomeTeam="Valencia", AwayTeam="Celta")
    staged, report = validate_new_matches(old_match, existing_path)
    assert report["rows_accepted_for_staging"] == 0
    assert report["rows_rejected_as_not_newer_than_training_data"] == 1


def test_validate_new_matches_raises_on_missing_critical_columns(tmp_path) -> None:
    existing_path = _existing_processed(tmp_path)
    incomplete = pd.DataFrame([{"Date": "20/01/2026", "HomeTeam": "Sevilla"}])
    with pytest.raises(ValueError):
        validate_new_matches(incomplete, existing_path)


def test_staging_never_touches_the_canonical_training_file(tmp_path) -> None:
    existing_path = _existing_processed(tmp_path)
    before = existing_path.read_text(encoding="utf-8")
    staged, _ = validate_new_matches(_new_raw_row(), existing_path)
    staging_path = tmp_path / "staging" / "pending_matches.csv"
    written = stage_new_matches(staged, staging_path)
    assert written == 1
    assert existing_path.read_text(encoding="utf-8") == before  # el training set no cambia
    assert staging_path.exists()


def test_staging_is_additive_and_deduplicates_by_match_id(tmp_path) -> None:
    staging_path = tmp_path / "staging" / "pending_matches.csv"
    existing_path = _existing_processed(tmp_path)
    staged_1, _ = validate_new_matches(_new_raw_row(), existing_path)
    stage_new_matches(staged_1, staging_path)
    staged_2, _ = validate_new_matches(_new_raw_row(FTHG=3, FTAG=0, FTR="H"), existing_path)
    stage_new_matches(staged_2, staging_path)
    result = pd.read_csv(staging_path)
    assert len(result) == 1  # mismo match_id -> se actualiza, no se duplica
    assert result.iloc[0]["result_ft"] == "H"
