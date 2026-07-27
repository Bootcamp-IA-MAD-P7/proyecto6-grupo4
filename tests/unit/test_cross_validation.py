from __future__ import annotations

import pandas as pd
import pytest
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_FEATURES, MODEL_NUMERIC_FEATURES
from src.data.laliga_loader import TARGET_COLUMN
from src.evaluation.cross_validation import chronological_cv_scores


def _build_tiny_pipeline():
    pre = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), list(MODEL_NUMERIC_FEATURES)),
        ("teams", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), list(MODEL_CATEGORICAL_FEATURES)),
    ])
    return Pipeline([("preprocessing", pre), ("classifier", LogisticRegression(max_iter=200, random_state=42))])


def _write_fake_features(tmp_path):
    rows = 120
    dates = pd.date_range("2020-01-01", periods=rows, freq="7D")
    frame = pd.DataFrame({
        "match_id": [f"m{i}" for i in range(rows)],
        "match_date": dates,
        "split": ["train"] * (rows - 10) + ["validation"] * 10,
        "home_team": (["A", "B", "C"] * ((rows // 3) + 1))[:rows],
        "away_team": (["B", "C", "A"] * ((rows // 3) + 1))[:rows],
        TARGET_COLUMN: (["H", "D", "A"] * ((rows // 3) + 1))[:rows],
        **{column: [float((index + row) % 5) for row in range(rows)] for index, column in enumerate(MODEL_FEATURES[2:])},
    })
    features_path = tmp_path / "features.csv"
    frame.to_csv(features_path, index=False)
    source_path = tmp_path / "source.csv"
    pd.DataFrame({"a": [1, 2, 3]}).to_csv(source_path, index=False)
    return features_path, source_path


def test_chronological_cv_never_touches_validation_or_test(tmp_path) -> None:
    features_path, source_path = _write_fake_features(tmp_path)
    summary = chronological_cv_scores(
        candidate_id="TEST",
        build_pipeline=_build_tiny_pipeline,
        features_path=features_path,
        source_dataset_path=source_path,
        n_splits=3,
    )
    assert summary["method"] == "TimeSeriesSplit_within_train_only"
    assert summary["n_folds_scored"] >= 1
    for fold in summary["folds"]:
        assert fold["train_rows"] + fold["test_rows"] <= 110  # nunca supera las filas de train
    assert 0.0 <= summary["macro_f1_mean"] <= 1.0
    assert summary["macro_f1_std"] >= 0.0


def test_chronological_cv_folds_grow_and_stay_ordered(tmp_path) -> None:
    features_path, source_path = _write_fake_features(tmp_path)
    summary = chronological_cv_scores(
        candidate_id="TEST",
        build_pipeline=_build_tiny_pipeline,
        features_path=features_path,
        source_dataset_path=source_path,
        n_splits=3,
    )
    train_sizes = [fold["train_rows"] for fold in summary["folds"]]
    assert train_sizes == sorted(train_sizes)  # ventana de train crece fold a fold


def test_chronological_cv_raises_on_missing_columns(tmp_path) -> None:
    bad_path = tmp_path / "bad.csv"
    pd.DataFrame({"only_one_column": [1, 2, 3]}).to_csv(bad_path, index=False)
    with pytest.raises(ValueError):
        chronological_cv_scores(
            candidate_id="TEST",
            build_pipeline=_build_tiny_pipeline,
            features_path=bad_path,
            source_dataset_path=bad_path,
            n_splits=3,
        )
