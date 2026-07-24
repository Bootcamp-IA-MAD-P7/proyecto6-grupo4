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

SOURCE_PROVENANCE = {
    HISTORICAL_FILENAME: {
        "source_name": "La Liga Complete Dataset",
        "publisher": "Kishan Kumar (Kaggle)",
        "source_page_url": "https://www.kaggle.com/datasets/kishan305/la-liga-results-19952020",
        "upstream_source_url": "https://www.football-data.co.uk/data.php",
        "acquisition": "Descarga manual del CSV consolidado publicado en Kaggle.",
        "license": "Data files © Original Authors (según la ficha de Kaggle).",
        "license_evidence_url": (
            "https://www.kaggle.com/datasets/kishan305/la-liga-results-19952020"
        ),
        "license_checked_at": "2026-07-23",
        "license_status": "no_open_license_public_redistribution_not_demonstrated",
        "open_license_identifier": None,
        "usage_assessment": (
            "El uso analítico para predicción de partidos es compatible con la finalidad "
            "declarada por la fuente aguas arriba, pero la ficha no concede una licencia "
            "abierta ni permiso explícito de redistribución."
        ),
        "redistribution_status": "not_authorized_without_explicit_permission",
        "repository_policy": "local_only_no_public_raw_or_row_level_derivatives",
        "provenance_confidence": "confirmed_by_filename_schema_and_dataset_card",
    },
    DETAILED_FILENAME: {
        "source_name": "Football-Data Spain La Liga 2025/2026 (SP1.csv)",
        "publisher": "Football-Data.co.uk",
        "source_page_url": "https://www.football-data.co.uk/data.php",
        "direct_download_url": "https://www.football-data.co.uk/mmz4281/2526/SP1.csv",
        "column_notes_url": "https://www.football-data.co.uk/notes.txt",
        "acquisition": (
            "Descarga del CSV SP1 de la temporada 2025/2026 y renombrado local. "
            "La copia raw corresponde a una instantánea anterior a la versión actualmente publicada."
        ),
        "license": (
            "Football-Data ofrece acceso gratuito y declara los datos para predicción de "
            "partidos de liga; no publica una licencia abierta ni un permiso explícito de "
            "redistribución."
        ),
        "license_evidence_url": "https://www.football-data.co.uk/data.php",
        "license_checked_at": "2026-07-23",
        "license_status": "no_open_license_public_redistribution_not_demonstrated",
        "open_license_identifier": None,
        "usage_assessment": (
            "El proyecto de predicción prepartido encaja con la finalidad publicada. Esto "
            "no equivale a autorización para republicar los archivos."
        ),
        "redistribution_status": "not_authorized_without_explicit_permission",
        "repository_policy": "local_only_no_public_raw_or_row_level_derivatives",
        "provenance_confidence": "confirmed_by_url_schema_season_and_380_match_rows",
    },
}

HISTORICAL_SOURCE_COLUMNS = [
    "Season",
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
    "HTHG",
    "HTAG",
    "HTR",
]

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

HISTORICAL_TO_CANONICAL = {
    "Season": "season_validation_only",
    "Date": "match_date",
    "HomeTeam": "home_team",
    "AwayTeam": "away_team",
    "FTHG": "home_goals_ft",
    "FTAG": "away_goals_ft",
    "FTR": "result_ft",
    "HTHG": "home_goals_ht",
    "HTAG": "away_goals_ht",
    "HTR": "result_ht",
}

DETAILED_SOURCE_COLUMNS = [
    "Div", "Date", "Time", "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
    "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR",
    "AvgH", "AvgD", "AvgA", "Avg>2.5", "Avg<2.5", "AHh", "AvgAHH", "AvgAHA",
    "AvgCH", "AvgCD", "AvgCA", "AvgC>2.5", "AvgC<2.5", "AHCh", "AvgCAHH", "AvgCAHA",
]

CRITICAL_SOURCE_COLUMNS = [
    "Date",
    "HomeTeam",
    "AwayTeam",
    "FTHG",
    "FTAG",
    "FTR",
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


def build_source_column_policy(
    historical: pd.DataFrame,
    detailed: pd.DataFrame,
) -> pd.DataFrame:
    """Explica, columna por columna, qué se conserva y qué se descarta."""

    rows: list[dict[str, Any]] = []
    for column in historical.columns:
        if column == "Season":
            action = "validate_then_derive"
            reason = (
                "Se usa para comprobar la temporada original; la salida se deriva de la fecha "
                "para aplicar una regla única a ambas fuentes."
            )
        else:
            action = "keep_and_rename"
            reason = "Campo mínimo necesario para identificar el partido, el marcador o el target."
        rows.append(
            {
                "source_file": HISTORICAL_FILENAME,
                "source_column": column,
                "action": action,
                "canonical_column": HISTORICAL_TO_CANONICAL.get(column, ""),
                "reason": reason,
            }
        )

    for column in detailed.columns:
        if column in DETAILED_SOURCE_COLUMNS:
            action = "keep_and_rename"
            canonical = SOURCE_TO_CANONICAL.get(column, column)
            if column in {"Div", "Date", "Time", "HomeTeam", "AwayTeam"}:
                reason = "Identificación, orden temporal o metadato mínimo del partido."
            elif column in {"FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR"}:
                reason = "Marcador y resultado necesarios para auditoría descriptiva y target."
            elif column in {
                "HS", "AS", "HST", "AST", "HF", "AF", "HC", "AC", "HY", "AY", "HR", "AR"
            }:
                reason = (
                    "Estadística agregada seleccionada para EDA; se marca como postpartido "
                    "y queda excluida del modelado prepartido."
                )
            else:
                reason = (
                    "Promedio de mercado seleccionado para evitar conservar decenas de cuotas "
                    "redundantes por casa de apuestas."
                )
        else:
            action = "drop"
            canonical = ""
            reason = (
                "Cuota específica, máxima o de exchange redundante respecto a los promedios "
                "seleccionados; aumenta dimensionalidad y presenta cobertura irregular."
            )
        rows.append(
            {
                "source_file": DETAILED_FILENAME,
                "source_column": column,
                "action": action,
                "canonical_column": canonical,
                "reason": reason,
            }
        )
    return pd.DataFrame(rows)


def _source_profile(frame: pd.DataFrame, filename: str) -> dict[str, Any]:
    return {
        "filename": filename,
        "rows": int(len(frame)),
        "columns": int(frame.shape[1]),
        "exact_duplicate_rows": int(frame.duplicated().sum()),
        "columns_with_missing": int(frame.isna().any().sum()),
        "missing_cells": int(frame.isna().sum().sum()),
    }


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
    _require_columns(historical, HISTORICAL_SOURCE_COLUMNS, HISTORICAL_FILENAME)
    _require_columns(detailed, DETAILED_SOURCE_COLUMNS, DETAILED_FILENAME)
    return historical, detailed


def _clean_source(
    frame: pd.DataFrame,
    filename: str,
    *,
    date_format: str | None = None,
    dayfirst: bool = False,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Normaliza una fuente y elimina solo registros inequívocamente inválidos."""

    cleaned = frame.copy()
    input_profile = _source_profile(cleaned, filename)
    string_columns = [
        column
        for column in ["Season", "Div", "Time", "HomeTeam", "AwayTeam", "FTR", "HTR"]
        if column in cleaned.columns
    ]
    for column in string_columns:
        cleaned[column] = cleaned[column].astype("string").str.strip()
    for column in ["FTR", "HTR"]:
        if column in cleaned:
            cleaned[column] = cleaned[column].str.upper()

    exact_duplicates = int(cleaned.duplicated().sum())
    cleaned = cleaned.drop_duplicates().copy()
    cleaned["_parsed_date"] = pd.to_datetime(
        cleaned["Date"],
        format=date_format,
        dayfirst=dayfirst,
        errors="coerce",
    )
    for column in ["FTHG", "FTAG"]:
        cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    invalid_date = cleaned["_parsed_date"].isna()
    missing_critical = cleaned[CRITICAL_SOURCE_COLUMNS].isna().any(axis=1)
    blank_teams = cleaned["HomeTeam"].eq("") | cleaned["AwayTeam"].eq("")
    invalid_target = ~cleaned["FTR"].isin({"H", "D", "A"})
    same_team = cleaned["HomeTeam"].eq(cleaned["AwayTeam"])
    negative_goals = cleaned["FTHG"].lt(0) | cleaned["FTAG"].lt(0)
    inconsistent_result = (
        (cleaned["FTHG"].gt(cleaned["FTAG"]) & cleaned["FTR"].ne("H"))
        | (cleaned["FTHG"].eq(cleaned["FTAG"]) & cleaned["FTR"].ne("D"))
        | (cleaned["FTHG"].lt(cleaned["FTAG"]) & cleaned["FTR"].ne("A"))
    )
    invalid = (
        invalid_date
        | missing_critical
        | blank_teams
        | invalid_target
        | same_team
        | negative_goals
        | inconsistent_result
    )
    invalid_rows = int(invalid.sum())
    cleaned = cleaned.loc[~invalid].copy()
    cleaned["_match_key"] = _match_key(
        cleaned["_parsed_date"], cleaned["HomeTeam"], cleaned["AwayTeam"]
    )
    duplicate_match_keys = int(cleaned["_match_key"].duplicated(keep="last").sum())
    cleaned = cleaned.drop_duplicates("_match_key", keep="last").copy()

    season_mismatches = 0
    if "Season" in cleaned:
        derived_season = _season_from_dates(cleaned["_parsed_date"])
        season_mismatches = int(
            cleaned["Season"].astype("string").reset_index(drop=True).ne(
                derived_season.reset_index(drop=True)
            ).sum()
        )

    report = {
        "input": input_profile,
        "exact_duplicate_rows_removed": exact_duplicates,
        "invalid_rows_removed": invalid_rows,
        "invalid_breakdown_before_union": {
            "invalid_date": int(invalid_date.sum()),
            "missing_critical": int(missing_critical.sum()),
            "blank_team": int(blank_teams.sum()),
            "invalid_target": int(invalid_target.sum()),
            "same_team": int(same_team.sum()),
            "negative_goals": int(negative_goals.sum()),
            "result_goal_inconsistency": int(inconsistent_result.sum()),
        },
        "duplicate_match_keys_removed": duplicate_match_keys,
        "season_mismatches_against_derived": season_mismatches,
        "rows_after_source_cleaning": int(len(cleaned)),
    }
    return cleaned, report


def preprocess_sources(
    historical: pd.DataFrame,
    detailed: pd.DataFrame,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Limpia, combina y documenta las dos fuentes raw."""

    column_policy = build_source_column_policy(historical, detailed)
    historical_input_columns = int(historical.shape[1])
    detailed_input_columns = int(detailed.shape[1])
    historical, historical_report = _clean_source(
        historical,
        HISTORICAL_FILENAME,
        dayfirst=True,
    )
    detailed, detailed_report = _clean_source(
        detailed,
        DETAILED_FILENAME,
        date_format="%Y-%m-%d",
    )
    detailed_keys = set(detailed["_match_key"])
    overlap_keys = set(historical["_match_key"]) & detailed_keys
    historical_only = historical.loc[~historical["_match_key"].isin(detailed_keys)].copy()

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
            "match_date": historical_only["Date"],
            "match_time": pd.Series(pd.NA, index=historical_only.index, dtype="string"),
            "home_team": historical_only["HomeTeam"],
            "away_team": historical_only["AwayTeam"],
            "home_goals_ft": historical_only["FTHG"],
            "away_goals_ft": historical_only["FTAG"],
            "result_ft": historical_only["FTR"],
            "home_goals_ht": historical_only["HTHG"],
            "away_goals_ht": historical_only["HTAG"],
            "result_ht": historical_only["HTR"],
            "_parsed_date": historical_only["_parsed_date"],
            "_match_key": historical_only["_match_key"],
            "source_coverage": "historical_only",
            "has_detailed_stats": False,
        },
        index=historical_only.index,
    )
    for canonical_name in [SOURCE_TO_CANONICAL[column] for column in DETAILED_SOURCE_COLUMNS[11:]]:
        historical_frame[canonical_name] = pd.NA

    combined = pd.concat([historical_frame, detailed_frame], ignore_index=True, sort=False)
    combined["season"] = _season_from_dates(combined["_parsed_date"])
    combined["match_id"] = (
        combined["_parsed_date"].dt.strftime("%Y-%m-%d")
        + "_"
        + combined["home_team"].map(_slug)
        + "_"
        + combined["away_team"].map(_slug)
    )
    combined["match_date"] = combined["_parsed_date"].dt.normalize()
    combined["match_time"] = combined["match_time"].astype("string")
    combined["match_year"] = combined["_parsed_date"].dt.year.astype("Int64")
    combined["match_month"] = combined["_parsed_date"].dt.month.astype("Int64")
    combined["iso_weekday"] = combined["_parsed_date"].dt.isocalendar().day.astype("Int64")

    for column in COUNT_COLUMNS:
        combined[column] = pd.to_numeric(combined[column], errors="coerce").astype("Int64")
    odds_columns = [
        column
        for column in CANONICAL_COLUMNS
        if column.startswith("odds_") or column.startswith("asian_handicap")
    ]
    for column in odds_columns:
        combined[column] = pd.to_numeric(combined[column], errors="coerce")

    combined["total_goals"] = (
        combined["home_goals_ft"] + combined["away_goals_ft"]
    ).astype("Int64")
    combined["goal_diff_home"] = (
        combined["home_goals_ft"] - combined["away_goals_ft"]
    ).astype("Int64")
    combined["both_teams_scored"] = (
        combined["home_goals_ft"].gt(0) & combined["away_goals_ft"].gt(0)
    ).astype("boolean")
    combined["over_2_5"] = combined["total_goals"].gt(2.5).astype("boolean")
    combined["clean_sheet_home"] = combined["away_goals_ft"].eq(0).astype("boolean")
    combined["clean_sheet_away"] = combined["home_goals_ft"].eq(0).astype("boolean")
    combined["home_points"] = combined["result_ft"].map({"H": 3, "D": 1, "A": 0}).astype("Int64")
    combined["away_points"] = combined["result_ft"].map({"H": 0, "D": 1, "A": 3}).astype("Int64")
    combined["has_detailed_stats"] = combined["has_detailed_stats"].astype("boolean")

    combined = (
        combined.sort_values(
            ["_parsed_date", "match_time", "home_team", "away_team"],
            na_position="last",
        )
        .loc[:, CANONICAL_COLUMNS]
        .reset_index(drop=True)
    )
    audit = audit_dataset(combined)
    if (
        audit["duplicate_match_ids"]
        or audit["full_time_result_inconsistencies"]
        or audit["missing_target"]
    ):
        raise ValueError(f"El dataset canónico no supera la auditoría: {audit}")

    report = {
        "pipeline_version": "laliga_preprocessing_v2",
        "join": {
            "type": "vertical_union_with_overlap_precedence",
            "key": ["normalized_match_date", "trimmed_home_team", "trimmed_away_team"],
            "why": (
                "Las fuentes describen la misma unidad (partido) con esquemas distintos. "
                "Una unión vertical preserva el histórico; para las claves repetidas se conserva "
                "la fila detallada porque contiene todas las variables del histórico más estadísticas "
                "y promedios de mercado."
            ),
            "overlap_rows": int(len(overlap_keys)),
            "historical_overlap_rows_discarded": int(len(overlap_keys)),
            "detailed_rows_prioritized": int(len(overlap_keys)),
        },
        "source_cleaning": {
            HISTORICAL_FILENAME: historical_report,
            DETAILED_FILENAME: detailed_report,
        },
        "column_policy_summary": {
            "historical_input_columns": historical_input_columns,
            "detailed_input_columns": detailed_input_columns,
            "detailed_columns_kept": int(len(DETAILED_SOURCE_COLUMNS)),
            "detailed_columns_dropped": int(
                (
                    column_policy["source_file"].eq(DETAILED_FILENAME)
                    & column_policy["action"].eq("drop")
                ).sum()
            ),
            "canonical_columns": int(len(CANONICAL_COLUMNS)),
        },
        "null_policy": {
            "critical_fields": CRITICAL_SOURCE_COLUMNS,
            "critical_rule": "remove_row_if_missing_or_invalid",
            "optional_half_time_rule": (
                "retain_missing; these fields are post-event and excluded from pre-match modeling"
            ),
            "historical_detailed_block_rule": (
                "retain_as_null; absence is structural and is not imputed"
            ),
        },
        "output": audit,
    }
    return combined, report


def build_canonical_dataset(historical: pd.DataFrame, detailed: pd.DataFrame) -> pd.DataFrame:
    """Combina ambas fuentes y devuelve una fila única por partido."""

    canonical, _ = preprocess_sources(historical, detailed)
    return canonical


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


def load_processed_dataset(processed_path: str | Path) -> pd.DataFrame:
    """Carga la salida limpia aplicando el mismo contrato de tipos."""

    path = Path(processed_path)
    if not path.exists():
        raise FileNotFoundError(
            f"No existe el dataset procesado: {path}. Ejecuta scripts/run_laliga_preprocessing.py."
        )
    frame = pd.read_csv(path, parse_dates=["match_date"])
    _require_columns(frame, CANONICAL_COLUMNS, path.name)
    frame = frame.loc[:, CANONICAL_COLUMNS].copy()
    string_columns = [
        "match_id",
        "season",
        "match_time",
        "home_team",
        "away_team",
        "result_ft",
        "result_ht",
        "source_coverage",
        "league_code",
    ]
    for column in string_columns:
        frame[column] = frame[column].astype("string")
    for column in COUNT_COLUMNS + [
        "match_year",
        "match_month",
        "iso_weekday",
        "total_goals",
        "goal_diff_home",
        "home_points",
        "away_points",
    ]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce").astype("Int64")
    for column in [
        "both_teams_scored",
        "over_2_5",
        "clean_sheet_home",
        "clean_sheet_away",
        "has_detailed_stats",
    ]:
        frame[column] = frame[column].astype("boolean")
    audit = audit_dataset(frame)
    if (
        audit["duplicate_match_ids"]
        or audit["missing_target"]
        or audit["full_time_result_inconsistencies"]
    ):
        raise ValueError(f"El dataset procesado no supera la auditoría: {audit}")
    return frame


def build_dataset_manifest(
    raw_dir: str | Path,
    canonical: pd.DataFrame,
    preprocessing_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Registra procedencia, huellas, transformación y dimensiones."""

    raw_path = Path(raw_dir)
    sources = []
    for filename in (HISTORICAL_FILENAME, DETAILED_FILENAME):
        path = raw_path / filename
        sources.append(
            {
                "filename": filename,
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
                **SOURCE_PROVENANCE[filename],
            }
        )
    return {
        "dataset_id": "laliga_matches_1995_96_to_2025_26_v1",
        "target_provisional": TARGET_COLUMN,
        "generated_from": sources,
        "preprocessing": preprocessing_report or {},
        "canonical_audit": audit_dataset(canonical),
        "provenance_status": (
            "team_ratified_local_or_private_repository_only_"
            "public_redistribution_not_authorized"
        ),
    }


def write_canonical_outputs(
    raw_dir: str | Path,
    processed_path: str | Path,
    manifest_path: str | Path,
    preprocessing_report_path: str | Path | None = None,
    column_policy_path: str | Path | None = None,
    provenance_path: str | Path | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Carga, prepara y persiste la copia procesada y su manifest versionable."""

    historical, detailed = load_raw_sources(raw_dir)
    canonical, preprocessing_report = preprocess_sources(historical, detailed)
    processed = Path(processed_path)
    processed.parent.mkdir(parents=True, exist_ok=True)
    canonical.to_csv(
        processed,
        index=False,
        encoding="utf-8",
        date_format="%Y-%m-%d",
    )
    preprocessing_report["output"].update(
        {
            "path": processed.as_posix(),
            "bytes": processed.stat().st_size,
            "sha256": file_sha256(processed),
        }
    )
    manifest = build_dataset_manifest(raw_dir, canonical, preprocessing_report)
    manifest_file = Path(manifest_path)
    manifest_file.parent.mkdir(parents=True, exist_ok=True)
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

    if preprocessing_report_path is not None:
        report_file = Path(preprocessing_report_path)
        report_file.parent.mkdir(parents=True, exist_ok=True)
        report_file.write_text(
            json.dumps(preprocessing_report, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    if column_policy_path is not None:
        policy_file = Path(column_policy_path)
        policy_file.parent.mkdir(parents=True, exist_ok=True)
        build_source_column_policy(historical, detailed).to_csv(
            policy_file,
            index=False,
            encoding="utf-8",
        )
    if provenance_path is not None:
        provenance_file = Path(provenance_path)
        provenance_file.parent.mkdir(parents=True, exist_ok=True)
        provenance_file.write_text(
            json.dumps(SOURCE_PROVENANCE, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    return canonical, manifest
