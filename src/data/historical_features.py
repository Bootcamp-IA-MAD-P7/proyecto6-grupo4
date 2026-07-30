"""Features prepartido comunes calculadas exclusivamente desde el pasado.

El módulo procesa los encuentros por lotes de ``match_date``. Todas las filas de
una fecha se describen usando el estado disponible al cierre de la fecha anterior
y solo después se incorporan sus resultados. Esto evita que dos partidos del
mismo día se filtren información entre sí cuando la hora de inicio no es fiable.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from src.data.laliga_loader import TARGET_COLUMN, file_sha256, load_processed_dataset
from src.evaluation.splits import assign_splits


FEATURE_GENERATOR_VERSION = "historical_features_v1"
FEATURE_OUTPUT_FILENAME = "laliga_historical_features_v1.csv"


@dataclass(frozen=True)
class HistoricalFeatureConfig:
    """Parámetros fijos y versionados del generador común."""

    rolling_window: int = 5
    initial_elo: float = 1500.0
    elo_k_factor: float = 20.0


MODEL_NUMERIC_FEATURES = (
    "home_matches_played",
    "away_matches_played",
    "home_points_per_match_5",
    "away_points_per_match_5",
    "home_goals_for_per_match_5",
    "away_goals_for_per_match_5",
    "home_goals_against_per_match_5",
    "away_goals_against_per_match_5",
    "home_win_rate_5",
    "away_win_rate_5",
    "home_elo_pre_match",
    "away_elo_pre_match",
    "elo_difference_home",
    "home_days_since_last_match",
    "away_days_since_last_match",
)
MODEL_CATEGORICAL_FEATURES = ("home_team", "away_team")
MODEL_FEATURES = MODEL_CATEGORICAL_FEATURES + MODEL_NUMERIC_FEATURES
FEATURE_METADATA_COLUMNS = ("match_id", "season", "match_date", "split", TARGET_COLUMN)
FEATURE_COLUMNS = FEATURE_METADATA_COLUMNS + MODEL_FEATURES
PRE_SPLIT_FEATURE_COLUMNS = tuple(column for column in FEATURE_COLUMNS if column != "split")


@dataclass
class _TeamState:
    rating: float
    matches_played: int = 0
    points: deque[float] | None = None
    goals_for: deque[float] | None = None
    goals_against: deque[float] | None = None
    wins: deque[float] | None = None
    last_match_date: pd.Timestamp | None = None

    @classmethod
    def create(cls, config: HistoricalFeatureConfig) -> "_TeamState":
        return cls(
            rating=config.initial_elo,
            points=deque(maxlen=config.rolling_window),
            goals_for=deque(maxlen=config.rolling_window),
            goals_against=deque(maxlen=config.rolling_window),
            wins=deque(maxlen=config.rolling_window),
        )


def _validate_input(frame: pd.DataFrame) -> pd.DataFrame:
    required = {
        "match_id", "season", "match_date", "home_team", "away_team",
        "home_goals_ft", "away_goals_ft", TARGET_COLUMN,
    }
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError(f"Faltan columnas para generar features históricas: {missing}")
    ordered = frame.copy()
    ordered["match_date"] = pd.to_datetime(ordered["match_date"], errors="coerce")
    if ordered["match_date"].isna().any():
        raise ValueError("match_date contiene fechas inválidas.")
    if ordered["match_id"].isna().any() or ordered["match_id"].duplicated().any():
        raise ValueError("match_id debe existir y ser único.")
    if ordered[["home_team", "away_team"]].isna().any().any() or ordered["home_team"].eq(ordered["away_team"]).any():
        raise ValueError("Los equipos deben existir y ser distintos.")
    if not ordered[TARGET_COLUMN].isin({"H", "D", "A"}).all():
        raise ValueError("result_ft debe contener únicamente H, D o A.")
    for column in ("home_goals_ft", "away_goals_ft"):
        ordered[column] = pd.to_numeric(ordered[column], errors="coerce")
    if ordered[["home_goals_ft", "away_goals_ft"]].isna().any().any():
        raise ValueError("Los goles finales son obligatorios para actualizar el histórico.")
    return ordered.sort_values(["match_date", "match_id"], kind="mergesort").reset_index(drop=True)


def _mean(values: deque[float] | None) -> float:
    return float(np.mean(values)) if values else 0.0


def _days_since(last_date: pd.Timestamp | None, current_date: pd.Timestamp) -> float:
    return float((current_date - last_date).days) if last_date is not None else -1.0


def _pre_match_row(
    row: pd.Series,
    home: _TeamState,
    away: _TeamState,
) -> dict[str, Any]:
    date = row["match_date"]
    return {
        "match_id": row["match_id"],
        "season": row["season"],
        "match_date": date,
        "home_team": row["home_team"],
        "away_team": row["away_team"],
        TARGET_COLUMN: row[TARGET_COLUMN],
        "home_matches_played": float(home.matches_played),
        "away_matches_played": float(away.matches_played),
        "home_points_per_match_5": _mean(home.points),
        "away_points_per_match_5": _mean(away.points),
        "home_goals_for_per_match_5": _mean(home.goals_for),
        "away_goals_for_per_match_5": _mean(away.goals_for),
        "home_goals_against_per_match_5": _mean(home.goals_against),
        "away_goals_against_per_match_5": _mean(away.goals_against),
        "home_win_rate_5": _mean(home.wins),
        "away_win_rate_5": _mean(away.wins),
        "home_elo_pre_match": home.rating,
        "away_elo_pre_match": away.rating,
        "elo_difference_home": home.rating - away.rating,
        "home_days_since_last_match": _days_since(home.last_match_date, date),
        "away_days_since_last_match": _days_since(away.last_match_date, date),
    }


def _result_points(result: str) -> tuple[float, float, float, float]:
    if result == "H":
        return 3.0, 0.0, 1.0, 0.0
    if result == "A":
        return 0.0, 3.0, 0.0, 1.0
    return 1.0, 1.0, 0.0, 0.0


def _update_after_match(
    row: pd.Series,
    home: _TeamState,
    away: _TeamState,
    config: HistoricalFeatureConfig,
) -> None:
    _update_team_states(
        home,
        away,
        result=row[TARGET_COLUMN],
        home_goals=float(row["home_goals_ft"]),
        away_goals=float(row["away_goals_ft"]),
        match_date=row["match_date"],
        config=config,
    )


def _update_team_states(
    home: _TeamState,
    away: _TeamState,
    *,
    result: str,
    home_goals: float,
    away_goals: float,
    match_date: pd.Timestamp,
    config: HistoricalFeatureConfig,
) -> None:
    home_points, away_points, home_win, away_win = _result_points(result)
    expected_home = 1.0 / (1.0 + 10.0 ** ((away.rating - home.rating) / 400.0))
    actual_home = 1.0 if result == "H" else 0.0 if result == "A" else 0.5
    rating_change = config.elo_k_factor * (actual_home - expected_home)
    home.rating += rating_change
    away.rating -= rating_change
    for state, points, goals_for, goals_against, win in (
        (home, home_points, home_goals, away_goals, home_win),
        (away, away_points, away_goals, home_goals, away_win),
    ):
        state.matches_played += 1
        state.points.append(points)
        state.goals_for.append(goals_for)
        state.goals_against.append(goals_against)
        state.wins.append(win)
        state.last_match_date = match_date


@dataclass
class HistoricalFeatureSnapshot:
    """Estado acumulado reutilizable para inferencias posteriores al histórico."""

    config: HistoricalFeatureConfig
    states: dict[str, _TeamState]

    @classmethod
    def from_frame(
        cls,
        frame: pd.DataFrame,
        config: HistoricalFeatureConfig | None = None,
    ) -> "HistoricalFeatureSnapshot":
        config = config or HistoricalFeatureConfig()
        ordered = _validate_input(frame)
        states: dict[str, _TeamState] = {}
        for row in ordered.itertuples(index=False):
            home = states.setdefault(row.home_team, _TeamState.create(config))
            away = states.setdefault(row.away_team, _TeamState.create(config))
            _update_team_states(
                home,
                away,
                result=getattr(row, TARGET_COLUMN),
                home_goals=float(row.home_goals_ft),
                away_goals=float(row.away_goals_ft),
                match_date=row.match_date,
                config=config,
            )
        return cls(config=config, states=states)

    def feature_row(
        self,
        home_team: str,
        away_team: str,
        match_date: pd.Timestamp,
    ) -> pd.DataFrame:
        """Construye una fila futura en O(1) sin recorrer otra vez los partidos."""

        if home_team not in self.states or away_team not in self.states:
            raise KeyError("Alguno de los equipos no existe en el snapshot histórico.")
        request = pd.Series(
            {
                "match_id": "__inference_request__",
                "season": "inference",
                "match_date": pd.Timestamp(match_date),
                "home_team": home_team,
                "away_team": away_team,
                TARGET_COLUMN: "D",
            }
        )
        values = _pre_match_row(
            request,
            self.states[home_team],
            self.states[away_team],
        )
        return pd.DataFrame([values]).loc[:, list(MODEL_FEATURES)]


def build_historical_features(
    frame: pd.DataFrame,
    config: HistoricalFeatureConfig | None = None,
) -> pd.DataFrame:
    """Devuelve las features comunes sin usar ningún resultado de su propia fecha.

    El dataframe de salida conserva ``match_id`` y el target solo como metadata;
    ambos están fuera de ``MODEL_FEATURES`` y ningún pipeline debe entrenar con ellos.
    """

    config = config or HistoricalFeatureConfig()
    if config.rolling_window < 1 or config.elo_k_factor <= 0:
        raise ValueError("rolling_window debe ser >= 1 y elo_k_factor debe ser positivo.")
    ordered = _validate_input(frame)
    states: dict[str, _TeamState] = {}
    feature_rows: list[dict[str, Any]] = []
    for _, day_rows in ordered.groupby("match_date", sort=False):
        # Snapshot por fecha: no hay actualización hasta calcular todas las filas del día.
        for _, row in day_rows.iterrows():
            home = states.setdefault(row["home_team"], _TeamState.create(config))
            away = states.setdefault(row["away_team"], _TeamState.create(config))
            feature_rows.append(_pre_match_row(row, home, away))
        for _, row in day_rows.iterrows():
            _update_after_match(row, states[row["home_team"]], states[row["away_team"]], config)
    return pd.DataFrame(feature_rows).loc[:, PRE_SPLIT_FEATURE_COLUMNS]


def _validate_splits(source: pd.DataFrame, splits: pd.DataFrame) -> pd.Series:
    required = {"match_id", "season", "split"}
    if set(splits.columns) != required or splits["match_id"].duplicated().any():
        raise ValueError("El archivo de splits no cumple el contrato match_id/season/split.")
    expected = assign_splits(source).astype("string")
    observed = source.loc[:, ["match_id", "season"]].merge(
        splits, on=["match_id", "season"], how="left", validate="one_to_one"
    )["split"].astype("string")
    if observed.isna().any() or not observed.eq(expected).all():
        raise ValueError("Los splits no cubren o no respetan la asignación congelada.")
    return pd.Series(observed.to_numpy(), index=source["match_id"].astype("string"))


def build_feature_manifest(
    source_path: str | Path,
    features_path: str | Path,
    features: pd.DataFrame,
    config: HistoricalFeatureConfig,
) -> dict[str, Any]:
    """Crea la evidencia versionada del contrato de features."""

    source = Path(source_path)
    output = Path(features_path)
    return {
        "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "generator_module": "src.data.historical_features",
        "parameters": asdict(config),
        "source_dataset": {"path": source.as_posix(), "sha256": file_sha256(source), "rows": int(len(features))},
        "features_output": {"path": output.as_posix(), "sha256": file_sha256(output), "rows": int(len(features))},
        "schema": {
            "metadata_columns_excluded_from_model": list(FEATURE_METADATA_COLUMNS),
            "categorical_model_features": list(MODEL_CATEGORICAL_FEATURES),
            "numeric_model_features": list(MODEL_NUMERIC_FEATURES),
        },
        "temporal_policy": "batch_by_match_date_then_update; strictly_prior_dates_only",
        "split_counts": {key: int(value) for key, value in features["split"].value_counts().sort_index().items()},
        "date_range": {
            "min": features["match_date"].min().strftime("%Y-%m-%d"),
            "max": features["match_date"].max().strftime("%Y-%m-%d"),
        },
    }


def generate_historical_features(
    processed_path: str | Path,
    splits_path: str | Path,
    features_output_path: str | Path,
    manifest_output_path: str | Path,
    config: HistoricalFeatureConfig | None = None,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Genera la tabla local y su manifest sin ajustar transformaciones de modelo."""

    config = config or HistoricalFeatureConfig()
    source = load_processed_dataset(processed_path)
    splits = pd.read_csv(splits_path, dtype={"match_id": "string", "season": "string", "split": "string"})
    features = build_historical_features(source, config)
    split_by_match_id = _validate_splits(source, splits)
    features["split"] = features["match_id"].astype("string").map(split_by_match_id)
    features = features.loc[:, FEATURE_COLUMNS]
    output = Path(features_output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(output, index=False, date_format="%Y-%m-%d")
    manifest = build_feature_manifest(processed_path, output, features, config)
    manifest_path = Path(manifest_output_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return features, manifest
