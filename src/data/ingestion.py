"""T-4.4: validación de partidos nuevos sin mezcla automática con entrenamiento.

Reutiliza la limpieza ya aprobada de `src/data/laliga_loader.py` (T-1.1/T-1.4)
para partidos nuevos en el mismo esquema raw (`Date`, `HomeTeam`, `AwayTeam`,
`FTHG`, `FTAG`, `FTR`, ...). No se modifica `laliga_loader.py`: este módulo
solo lo consume.

Los partidos validados se escriben en un área de staging
(`data/processed/staging/pending_matches.csv`), nunca en
`data/processed/laliga_matches_clean.csv`. Incorporarlos al entrenamiento
requiere un paso manual y explícito aparte (fuera de este módulo), tal como
exige el criterio de aceptación de T-4.4.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from src.data.laliga_loader import (
    CRITICAL_SOURCE_COLUMNS,
    TARGET_COLUMN,
    _clean_source,
    _slug,
    load_processed_dataset,
)

STAGING_COLUMNS = [
    "match_id",
    "match_date",
    "home_team",
    "away_team",
    "home_goals_ft",
    "away_goals_ft",
    "result_ft",
]


def validate_new_matches(
    new_raw: pd.DataFrame,
    existing_processed_path: str | Path,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Limpia y valida partidos nuevos; rechaza los que ya existen en el histórico.

    No toca `existing_processed_path`: solo lo lee para detectar duplicados.
    """

    missing = sorted(set(CRITICAL_SOURCE_COLUMNS) - set(new_raw.columns))
    if missing:
        raise ValueError(f"Los partidos nuevos no tienen las columnas mínimas: {missing}")

    cleaned, cleaning_report = _clean_source(new_raw, "incoming_new_matches.csv", dayfirst=True)
    if cleaned.empty:
        staged = pd.DataFrame(columns=STAGING_COLUMNS)
        return staged, {
            "rows_submitted": int(len(new_raw)),
            "rows_after_source_cleaning": 0,
            "rows_rejected_as_duplicates_of_training_data": 0,
            "rows_accepted_for_staging": 0,
            "cleaning_report": cleaning_report,
        }

    cleaned["match_id"] = (
        cleaned["_parsed_date"].dt.strftime("%Y-%m-%d")
        + "_"
        + cleaned["HomeTeam"].map(_slug)
        + "_"
        + cleaned["AwayTeam"].map(_slug)
    )

    existing = load_processed_dataset(existing_processed_path)
    known_match_ids = set(existing["match_id"])
    max_known_date = existing["match_date"].max()

    duplicate_mask = cleaned["match_id"].isin(known_match_ids)
    future_or_present_mask = cleaned["_parsed_date"] > max_known_date
    accepted_mask = ~duplicate_mask & future_or_present_mask
    accepted = cleaned.loc[accepted_mask].copy()

    staged = pd.DataFrame(
        {
            "match_id": accepted["match_id"],
            "match_date": accepted["_parsed_date"].dt.strftime("%Y-%m-%d"),
            "home_team": accepted["HomeTeam"],
            "away_team": accepted["AwayTeam"],
            "home_goals_ft": accepted["FTHG"],
            "away_goals_ft": accepted["FTAG"],
            "result_ft": accepted["FTR"],
        }
    ).reset_index(drop=True)

    report = {
        "rows_submitted": int(len(new_raw)),
        "rows_after_source_cleaning": int(len(cleaned)),
        "rows_rejected_as_duplicates_of_training_data": int(duplicate_mask.sum()),
        "rows_rejected_as_not_newer_than_training_data": int((~future_or_present_mask & ~duplicate_mask).sum()),
        "rows_accepted_for_staging": int(len(staged)),
        "max_known_training_date": max_known_date.strftime("%Y-%m-%d"),
        "cleaning_report": cleaning_report,
    }
    return staged, report


def stage_new_matches(staged: pd.DataFrame, staging_path: str | Path) -> int:
    """Añade partidos ya validados al área de staging, sin duplicarlos ni tocar el training set."""

    path = Path(staging_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.stat().st_size > 0:
        existing_staged = pd.read_csv(path)
        combined = pd.concat([existing_staged, staged], ignore_index=True)
        combined = combined.drop_duplicates("match_id", keep="last")
    else:
        combined = staged
    combined.to_csv(path, index=False, encoding="utf-8")
    return int(len(staged))
