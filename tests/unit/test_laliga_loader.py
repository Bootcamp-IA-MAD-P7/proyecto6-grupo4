from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.data.laliga_loader import (
    DETAILED_FILENAME,
    SOURCE_PROVENANCE,
    audit_dataset,
    build_canonical_dataset,
    build_source_column_policy,
    load_processed_dataset,
    preprocess_sources,
)


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


def test_preprocessing_reports_overlap_and_column_policy() -> None:
    detailed = _detailed().assign(B365H=2.1)

    result, report = preprocess_sources(_historical(), detailed)
    policy = build_source_column_policy(_historical(), detailed)

    assert len(result) == 2
    assert report["join"]["overlap_rows"] == 1
    assert report["column_policy_summary"]["detailed_columns_dropped"] == 1
    dropped = policy.loc[
        policy["source_file"].eq(DETAILED_FILENAME)
        & policy["source_column"].eq("B365H")
    ].iloc[0]
    assert dropped["action"] == "drop"


def test_preprocessing_removes_exact_duplicate_and_invalid_rows() -> None:
    historical = pd.concat(
        [
            _historical(),
            _historical().iloc[[0]],
            pd.DataFrame(
                [["2024-25", "20-05-2025", "Bad", "Bad", 1, 0, "H", 0, 0, "D"]],
                columns=_historical().columns,
            ),
        ],
        ignore_index=True,
    )

    result, report = preprocess_sources(historical, _detailed())

    cleaning = report["source_cleaning"]["LaLiga_Matches.csv"]
    assert len(result) == 2
    assert cleaning["exact_duplicate_rows_removed"] == 1
    assert cleaning["invalid_rows_removed"] == 1


def test_preprocessing_normalizes_known_team_name_typos() -> None:
    historical = pd.DataFrame(
        [
            ["1998-99", "31-08-1998", "Real Madrid", "Villareal", 4, 1, "H", 1, 1, "D"],
            ["2000-01", "10-09-2000", "Villarreal", "Celta", 1, 1, "D", 1, 1, "D"],
        ],
        columns=["Season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR"],
    )

    result, _ = preprocess_sources(historical, _detailed())

    teams = set(result["home_team"]) | set(result["away_team"])
    assert "Villareal" not in teams
    assert "Villarreal" in teams


def test_processed_csv_round_trip_preserves_contract(tmp_path: Path) -> None:
    expected = build_canonical_dataset(_historical(), _detailed())
    path = tmp_path / "clean.csv"
    expected.to_csv(path, index=False, date_format="%Y-%m-%d")

    loaded = load_processed_dataset(path)

    assert loaded.shape == expected.shape
    assert audit_dataset(loaded)["duplicate_match_ids"] == 0
    assert loaded["has_detailed_stats"].dtype.name == "boolean"


def test_source_policy_documents_unconfirmed_license_and_team_risk_acceptance() -> None:
    # Las fuentes no tienen licencia abierta confirmada del proveedor original,
    # pero el equipo ratifico explicitamente el riesgo de mantener los CSV
    # publicos en el repositorio (T-0.2b, daily 2026-07-24; reafirmado 2026-07-30).
    # No es una autorizacion del proveedor: es la decision de riesgo del equipo.
    assert set(SOURCE_PROVENANCE) == {
        "LaLiga_Matches.csv",
        "laliga_2025_2026_stats.csv",
    }
    for source in SOURCE_PROVENANCE.values():
        assert source["license_checked_at"] == "2026-07-23"
        assert source["open_license_identifier"] is None
        assert source["redistribution_status"] == "not_authorized_without_explicit_permission"
        assert source["repository_policy"] == "public_repository_team_accepted_risk"
        assert source["team_risk_acceptance"]["status"] == "ratified"
