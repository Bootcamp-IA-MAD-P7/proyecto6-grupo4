from __future__ import annotations

import json
from datetime import date

import joblib
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_FEATURES, MODEL_NUMERIC_FEATURES
from src.data.laliga_loader import CANONICAL_COLUMNS, TARGET_COLUMN
from src.inference.champion import ChampionPredictor, InferenceError


def _build_fitted_pipeline(train: pd.DataFrame) -> Pipeline:
    pre = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), list(MODEL_NUMERIC_FEATURES)),
        ("teams", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), list(MODEL_CATEGORICAL_FEATURES)),
    ])
    pipeline = Pipeline([("preprocessing", pre), ("classifier", LogisticRegression(max_iter=200, random_state=42))])
    pipeline.fit(train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    return pipeline


def _write_dataset_and_artifact(tmp_path):
    rows = 30
    dates = pd.date_range("2024-01-01", periods=rows, freq="7D")
    frame = pd.DataFrame({column: pd.Series(dtype="object") for column in CANONICAL_COLUMNS})
    frame["match_id"] = [f"m{i}" for i in range(rows)]
    frame["season"] = "2023-24"
    frame["match_date"] = dates
    frame["home_team"] = (["Real Madrid", "Barcelona", "Sevilla"] * (rows // 3))
    frame["away_team"] = (["Barcelona", "Sevilla", "Real Madrid"] * (rows // 3))
    frame[TARGET_COLUMN] = (["H", "D", "A"] * (rows // 3))
    goals_by_result = {"H": (1, 0), "D": (1, 1), "A": (0, 1)}
    frame["home_goals_ft"] = [goals_by_result[result][0] for result in frame[TARGET_COLUMN]]
    frame["away_goals_ft"] = [goals_by_result[result][1] for result in frame[TARGET_COLUMN]]
    dataset_path = tmp_path / "dataset.csv"
    frame.to_csv(dataset_path, index=False, date_format="%Y-%m-%d")

    train_features = pd.DataFrame({
        "home_team": frame["home_team"],
        "away_team": frame["away_team"],
        **{column: [float(i % 5) for i in range(rows)] for column in MODEL_FEATURES[2:]},
        TARGET_COLUMN: frame[TARGET_COLUMN],
    })
    pipeline = _build_fitted_pipeline(train_features)
    artifact_path = tmp_path / "champion.joblib"
    joblib.dump(pipeline, artifact_path)

    metadata_path = tmp_path / "champion_metadata.json"
    metadata_path.write_text(json.dumps({"champion_model_version": "test_v1", "source_data_sha256": "sha"}), encoding="utf-8")
    return dataset_path, artifact_path, metadata_path


def test_predictor_raises_team_not_found_for_unknown_team(tmp_path) -> None:
    dataset_path, artifact_path, metadata_path = _write_dataset_and_artifact(tmp_path)
    predictor = ChampionPredictor(dataset_path, artifact_path, metadata_path)
    with pytest.raises(InferenceError) as exc_info:
        predictor.predict("Equipo Inexistente", "Barcelona", date(2024, 6, 1))
    assert exc_info.value.code == "TEAM_NOT_FOUND"
    assert exc_info.value.status_code == 404


def test_predictor_raises_insufficient_history_before_any_known_match(tmp_path) -> None:
    dataset_path, artifact_path, metadata_path = _write_dataset_and_artifact(tmp_path)
    predictor = ChampionPredictor(dataset_path, artifact_path, metadata_path)
    with pytest.raises(InferenceError) as exc_info:
        predictor.predict("Real Madrid", "Barcelona", date(1990, 1, 1))
    assert exc_info.value.code == "INSUFFICIENT_HISTORY"
    assert exc_info.value.status_code == 409


def test_predictor_raises_model_unavailable_when_artifact_missing(tmp_path) -> None:
    dataset_path, artifact_path, metadata_path = _write_dataset_and_artifact(tmp_path)
    missing_artifact = tmp_path / "does_not_exist.joblib"
    with pytest.raises(InferenceError) as exc_info:
        ChampionPredictor(dataset_path, missing_artifact, metadata_path)
    assert exc_info.value.code == "MODEL_UNAVAILABLE"
    assert exc_info.value.status_code == 503


def test_predictor_succeeds_for_a_known_team_and_valid_future_date(tmp_path) -> None:
    dataset_path, artifact_path, metadata_path = _write_dataset_and_artifact(tmp_path)
    predictor = ChampionPredictor(dataset_path, artifact_path, metadata_path)
    result = predictor.predict("Real Madrid", "Barcelona", date(2024, 6, 1))
    assert result["prediction"] in {"H", "D", "A"}
    assert abs((result["H"] + result["D"] + result["A"]) - 1.0) < 1e-6
