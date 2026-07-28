"""Construcción prepartido y carga segura del Champion serializado."""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from src.data.historical_features import (
    MODEL_FEATURES,
    HistoricalFeatureSnapshot,
    build_historical_features,
)
from src.data.laliga_loader import TARGET_COLUMN, load_processed_dataset


class InferenceError(Exception):
    def __init__(self, code: str, message: str, status_code: int) -> None:
        self.code, self.message, self.status_code = code, message, status_code
        super().__init__(message)


class ChampionPredictor:
    """Mismo schema de features que entrenamiento, calculado solo con pasado."""

    def __init__(self, dataset_path: str | Path, artifact_path: str | Path, metadata_path: str | Path) -> None:
        self.history = load_processed_dataset(dataset_path)
        self.artifact_path = Path(artifact_path)
        self.metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
        if not self.artifact_path.exists():
            raise InferenceError("MODEL_UNAVAILABLE", "El Champion no está disponible.", 503)
        self.pipeline = joblib.load(self.artifact_path)
        self.teams = set(self.history["home_team"]) | set(self.history["away_team"])
        self.latest_history_date = self.history["match_date"].max()
        self.latest_snapshot = HistoricalFeatureSnapshot.from_frame(self.history)

    def feature_row(self, home_team: str, away_team: str, match_date: date) -> pd.DataFrame:
        if home_team not in self.teams or away_team not in self.teams:
            raise InferenceError("TEAM_NOT_FOUND", "Alguno de los equipos no pertenece al catálogo disponible.", 404)
        timestamp = pd.Timestamp(match_date)
        if timestamp > self.latest_history_date:
            return self.latest_snapshot.feature_row(
                home_team,
                away_team,
                timestamp,
            )
        prior = self.history.loc[self.history["match_date"] < timestamp].copy()
        if prior.empty:
            raise InferenceError("INSUFFICIENT_HISTORY", "No existe historial anterior para la fecha solicitada.", 409)
        request = pd.DataFrame([{
            "match_id": "__inference_request__", "season": "inference", "match_date": timestamp,
            "home_team": home_team, "away_team": away_team, "home_goals_ft": 0, "away_goals_ft": 0,
            TARGET_COLUMN: "D",
        }])
        # El generador agrupa la fecha: la fila sintética no ve resultados del mismo día.
        minimal = prior.loc[:, ["match_id", "season", "match_date", "home_team", "away_team", "home_goals_ft", "away_goals_ft", TARGET_COLUMN]]
        feature_table = build_historical_features(pd.concat([minimal, request], ignore_index=True))
        return feature_table.loc[feature_table["match_id"].eq("__inference_request__"), list(MODEL_FEATURES)]

    def predict(self, home_team: str, away_team: str, match_date: date) -> dict[str, float | str]:
        row = self.feature_row(home_team, away_team, match_date)
        probabilities = self.pipeline.predict_proba(row)[0]
        by_class = dict(zip(self.pipeline.classes_, probabilities, strict=True))
        prediction = max(by_class, key=by_class.get)
        return {"prediction": str(prediction), **{label: float(by_class[label]) for label in ("H", "D", "A")}}
