"""Carga única y preparación reproducible del dataset canónico de LaLiga.

El módulo no modifica los CSV originales. Combina el histórico con la fuente
detallada de 2025-26, elimina solapamientos exactos y añade variables derivadas
de uso analítico. El target provisional es ``result_ft`` (H/D/A).
"""

from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


HISTORICAL_FILENAME = "LaLiga_Matches.csv"
DETAILED_FILENAME = "laliga_2025_2026_stats.csv"
TARGET_COLUMN = "result_ft"

SOURCE_TO_CANONICAL = {
    "Div": "league_code",
    "Date": "match_date",
    "Time": "match_time",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals_ft",
    "FTAG": "away_goals_ft",
    "FTR": "result_ft",
    "HTHG": "home_goals_ht",
    "HTAG": "away_goals_ht",
    "HTR": "result_ht",
    "HS": "shots_home",
    "AS": "shots_away",
    "HST": "shots_on_target_home",
    "AST": "shots_on_target_away",
    "HF": "fouls_home",
    "AF": "fouls_away",
    "HC": "corners_home",
    "AC": "corners_away",
    "HY": "yellow_cards_home",
    "AY": "yellow_cards_away",
    "HR": "red_cards_home",
    "AR": "red_cards_away",
    "AvgH": "odds_avg_home_open",
    "AvgD": "odds_avg_draw_open",
    "AvgA": "odds_avg_away_open",
    "Avg>2.5": "odds_avg_over_2_5_open",
    "Avg<2.5": "odds_avg_under_2_5_open",
    "AHh": "asian_handicap_line_open",
    "AvgAHH": "odds_avg_asian_home_open",
    "AvgAHA": "odds_avg_asian_away_open",
    "AvgCH": "odds_avg_home_close",
    "AvgCD": "odds_avg_draw_close",
    "AvgCA": "odds_avg_away_close",
    "AvgC>2.5": "odds_avg_over_2_5_close",
    "AvgC<2.5": "odds_avg_under_2_5_close",
    "AHCh": "asian_handicap_line_close",
    "AvgCAHH": "odds_avg_asian_home_close",
    "AvgCAHA": "odds_avg_asian_away_close",
}

DETAILED_SOURCE_COLUMNS = [
    "Div", "Date", "Time", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
    "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR",
    "AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5", "AHh", "AvgAHH", "AvgAHA",
    "AvgCH", "AvgCD", "AvgCA", "AvgC>2.5", "AvgC<2.5", "AHCh", "AvgCAHH", "AvgCAHA",
]

DERIVED_COLUMNS = [
    "match_year", "match_month", "iso_weekday", "total_goals", "goal_diff_home",
    "both_teams_scored", "over_2_5", "clean_sheet_home", "clean_sheet_away",
    "home_points", "away_points",
]

CANONICAL_COLUMNS = [
    "match_id", "season", "match_date", "match_time", "match_year", "match_month", "iso_weekday",
    "home_team", "away_team", "home_goals_ft", "away_goals_ft", "result_ft",
    "home_goals_ht", "away_goals_ht", "result_ht", "total_goals", "goal_diff_home",
    "both_teams_scored", "over_2_5", "clean_sheet_home", "clean_sheet_away",
    "home_points", "away_points", "source_coverage", "has_detailed_stats", "league_code",
] + [SOURCE_TO_CANONICAL[column] for column in DETAILED_SOURCE_COLUMNS[11:]]

COUNT_COLUMNS = [
    "home_goals_ft", "away_goals_ft", "home_goals_ht", "away_goals_ht",
    "shots_home", "shots_away", "shots_on_target_home", "shots_on_target_away",
    "fouls_home", "fouls_away", "corners_home", "corners_away",
    "yellow_cards_home", "yellow_cards_away", "red_cards_home", "red_cards_away",
]


def _slug(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "_", normalized.lower()).strip("_")


def _season_from_dates(dates: pd.Series) -> pd.Series:
    start_year = np.where(dates.dt.month >= 7, dates.dt.year, dates.dt.year - 1)
    return pd.Series(
        [f"{int(year)}-{str(int(year) + 1)[-2:]}" for year in start_year],
        index=dates.index,
        dtype="string",
    )


def _match_key(dates: pd.Series, home: pd.Series, away: pd.Series) -> pd.Series:
    return dates.dt.strftime("%Y-%m-%d") + "|" + home.astype("string") + "|" + away.astype("string")


def _require_columns(frame: pd.DataFrame, required: list[str], source_name: str) -> None:
    missing = sorted(set(required) - set(frame.columns))
    if missing:
        raise ValueError(f"{source_name} no contiene las columnas requeridas: {missing}")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_raw_sources(raw_dir: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga los dos CSV originales desde un único directorio inmutable."""

    raw_path = Path(raw_dir)
    historical_path = raw_path / HISTORICAL_FILENAME
    detailed_path = raw_path / DETAILED_FILENAME
    missing_files = [str(path) for path in (historical_path, detailed_path) if not path.exists()]
    if missing_files:
        raise FileNotFoundError(
            "Faltan fuentes raw. Copia los CSV sin modificarlos en data/raw: " + ", ".join(missing_files)
        )
    historical = pd.read_csv(historical_path)
    detailed = pd.read_csv(detailed_path)
    _require_columns(
        historical,
        ["Season", "Date", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR"],
        HISTORICAL_FILENAME,
    )
    _require_columns(detailed, DETAILED_SOURCE_COLUMNS, DETAILED_FILENAME)
    return historical, detailed


def build_canonical_dataset(historical: pd.DataFrame, detailed: pd.DataFrame) -> pd.DataFrame:
    """Combina ambas fuentes y devuelve una fila única por partido."""

    historical = historical.copy()
    detailed = detailed.copy()
    historical["_parsed_date"] = pd.to_datetime(historical["Date"], dayfirst=True, errors="raise")
    detailed["_parsed_date"] = pd.to_datetime(detailed["Date"], format="%Y-%m-%d", errors="raise")
    historical["_match_key"] = _match_key(
        historical["_parsed_date"], historical["HomeTeam"], historical["AwayTeam"]
    )
    detailed["_match_key"] = _match_key(detailed["_parsed_date"], detailed["HomeTeam"], detailed["AwayTeam"])
    detailed_keys = set(detailed["_match_key"])
    overlap_keys = set(historical["_match_key"]) & detailed_keys
    historical = historical.loc[~historical["_match_key"].isin(detailed_keys)].copy()

    detailed_frame = detailed[DETAILED_SOURCE_COLUMNS].rename(columns=SOURCE_TO_CANONICAL).copy()
    detailed_frame["_parsed_date"] = detailed["_parsed_date"].to_numpy()
    detailed_frame["_match_key"] = detailed["_match_key"].to_numpy()
    detailed_frame["source_coverage"] = np.where(
        detailed_frame["_match_key"].isin(overlap_keys), "both_sources", "detailed_only"
    )
    detailed_frame["has_detailed_stats"] = True

    historical_frame = pd.DataFrame(
        {
            "league_code": "SP1",
            "match_date": historical["Date"],
            "match_time": pd.Series(pd.NA, index=historical.index, dtype="string"),
            "home_team": historical["HomeTeam"],
            "away_team": historical["AwayTeam"],
            "home_goals_ft": historical["FTHG"],
            "away_goals_ft": historical["FTAG"],
            "result_ft": historical["FTR"],
            "home_goals_ht": historical["HTHG"],
            "away_goals_ht": historical["HTAG"],
            "result_ht": historical["HTR"],
            "_parsed_date": historical["_parsed_date"],
            "_match_key": historical["_match_key"],
            "source_coverage": "historical_only",
            "has_detailed_stats": False,
        },
        index=historical.index,
    )
    for canonical_name in [SOURCE_TO_CANONICAL[column] for column in DETAILED_SOURCE_COLUMNS[11:]]:
        historical_frame[canonical_name] = pd.NA

    combined = pd.concat([historical_frame, detailed_frame], ignore_index=True, sort=False)
    combined["season"] = _season_from_dates(combined["_parsed_date"])
    combined["match_id"] = (
        combined["_parsed_date"].dt.strftime("%Y-%m-%d")
        + "_" + combined["home_team"].map(_slug) + "_" + combined["away_team"].map(_slug)
    )
    combined["match_date"] = combined["_parsed_date"].dt.normalize()
    combined["match_time"] = combined["match_time"].astype("string")
    combined["match_year"] = combined["_parsed_date"].dt.year.astype("Int64")
    combined["match_month"] = combined["_parsed_date"].dt.month.astype("Int64")
    combined["iso_weekday"] = combined["_parsed_date"].dt.isocalendar().day.astype("Int64")

    for column in COUNT_COLUMNS:
        combined[column] = pd.to_numeric(combined[column], errors="coerce").astype("Int64")
    odds_columns = [
        column for column in CANONICAL_COLUMNS
        if column.startswith("odds_") or column.startswith("asian_handicap")
    ]
    for column in odds_columns:
        combined[column] = pd.to_numeric(combined[column], errors="coerce")

    combined["total_goals"] = (combined["home_goals_ft"] + combined["away_goals_ft"]).astype("Int64")
    combined["goal_diff_home"] = (combined["home_goals_ft"] - combined["away_goals_ft"]).astype("Int64")
    combined["both_teams_scored"] = (
        (combined["home_goals_ft"] > 0) & (combined["away_goals_ft"] > 0)
    ).astype("boolean")
    combined["over_2_5"] = (combined["total_goals"] > 2.5).astype("boolean")
    combined["clean_sheet_home"] = (combined["away_goals_ft"] == 0).astype("boolean")
    combined["clean_sheet_away"] = (combined["home_goals_ft"] == 0).astype("boolean")
    combined["home_points"] = combined["result_ft"].map({"H": 3, "D": 1, "A": 0}).astype("Int64")
    combined["away_points"] = combined["result_ft"].map({"H": 0, "D": 1, "A": 3}).astype("Int64")
    combined["has_detailed_stats"] = combined["has_detailed_stats"].astype("boolean")

    combined = (
        combined.sort_values(["_parsed_date", "match_time", "home_team", "away_team"], na_position="last")
        .loc[:, CANONICAL_COLUMNS]
        .reset_index(drop=True)
    )
    audit = audit_dataset(combined)
    if audit["duplicate_match_ids"] or audit["full_time_result_inconsistencies"]:
        raise ValueError(f"El dataset canónico no supera la auditoría: {audit}")
    return combined


def audit_dataset(frame: pd.DataFrame) -> dict[str, Any]:
    """Calcula las comprobaciones de calidad que deben permanecer estables."""

    result_inconsistent = (
        ((frame["home_goals_ft"] > frame["away_goals_ft"]) & frame["result_ft"].ne("H"))
        | ((frame["home_goals_ft"] == frame["away_goals_ft"]) & frame["result_ft"].ne("D"))
        | ((frame["home_goals_ft"] < frame["away_goals_ft"]) & frame["result_ft"].ne("A"))
    )
    return {
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "season_count": int(frame["season"].nunique()),
        "date_min": frame["match_date"].min().strftime("%Y-%m-%d"),
        "date_max": frame["match_date"].max().strftime("%Y-%m-%d"),
        "duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_match_ids": int(frame["match_id"].duplicated().sum()),
        "missing_target": int(frame[TARGET_COLUMN].isna().sum()),
        "missing_half_time_rows": int(
            frame[["home_goals_ht", "away_goals_ht", "result_ht"]].isna().any(axis=1).sum()
        ),
        "full_time_result_inconsistencies": int(result_inconsistent.sum()),
        "invalid_target_values": sorted(set(frame[TARGET_COLUMN].dropna()) - {"H", "D", "A"}),
        "same_team_rows": int(frame["home_team"].eq(frame["away_team"]).sum()),
        "negative_goal_rows": int(
            ((frame["home_goals_ft"] < 0) | (frame["away_goals_ft"] < 0)).sum()
        ),
        "detailed_rows": int(frame["has_detailed_stats"].sum()),
        "source_coverage": {
            str(key): int(value) for key, value in frame["source_coverage"].value_counts().items()
        },
    }


def build_dataset_manifest(raw_dir: str | Path, canonical: pd.DataFrame) -> dict[str, Any]:
    """Registra huellas y dimensiones sin versionar los datos originales."""

    raw_path = Path(raw_dir)
    sources = []
    for filename in (HISTORICAL_FILENAME, DETAILED_FILENAME):
        path = raw_path / filename
        sources.append({"filename": filename, "bytes": path.stat().st_size, "sha256": file_sha256(path)})
    return {
        "dataset_id": "laliga_matches_1995_96_to_2025_26_v1",
        "target_provisional": TARGET_COLUMN,
        "generated_from": sources,
        "canonical_audit": audit_dataset(canonical),
        "provenance_status": "pending_source_and_license_confirmation",
    }


def write_canonical_outputs(
    raw_dir: str | Path,
    processed_path: str | Path,
    manifest_path: str | Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Carga, prepara y persiste la copia procesada y su manifest versionable."""

    historical, detailed = load_raw_sources(raw_dir)
    canonical = build_canonical_dataset(historical, detailed)
    processed = Path(processed_path)
    processed.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_csv(processed, index=False, encoding="utf-8")
    manifest = build_dataset_manifest(raw_dir, canonical)
    manifest_file = Path(manifest_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return canonical, manifest
