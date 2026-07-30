from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from src.data.historical_features import MODEL_FEATURES
from src.ensemble.svc_calibrated import (
    build_calibrated_svc,
    train_calibrated_svc,
)


def _features(rows: int = 60) -> pd.DataFrame:
    labels = np.resize(np.array(["H", "D", "A"]), rows)
    splits = np.array(["train"] * (rows - 15) + ["validation"] * 15)
    frame = pd.DataFrame(
        {
            "match_id": [f"m{index:03d}" for index in range(rows)],
            "match_date": pd.date_range("2020-01-01", periods=rows, freq="D"),
            "split": splits,
            "result_ft": labels,
            "home_team": np.resize(np.array(["Alpha", "Beta", "Gamma"]), rows),
            "away_team": np.resize(np.array(["Beta", "Gamma", "Alpha"]), rows),
        }
    )
    for index, column in enumerate(MODEL_FEATURES[2:]):
        frame[column] = np.arange(rows, dtype=float) + index
    return frame


def test_calibrated_svc_wraps_a_non_probabilistic_rbf_svc() -> None:
    calibrated = build_calibrated_svc(n_splits=3, n_jobs=1)

    assert isinstance(calibrated, CalibratedClassifierCV)
    assert calibrated.method == "temperature"
    assert calibrated.ensemble is False
    assert isinstance(calibrated.cv, StratifiedKFold)
    assert calibrated.cv.n_splits == 3
    assert isinstance(calibrated.estimator, Pipeline)
    classifier = calibrated.estimator.named_steps["classifier"]
    assert isinstance(classifier, SVC)
    assert classifier.kernel == "rbf"
    assert not hasattr(classifier, "predict_proba")


def test_training_writes_calibrated_probabilities_without_test(tmp_path: Path) -> None:
    features = _features()
    features_path = tmp_path / "features.csv"
    features.to_csv(features_path, index=False)
    metrics_path = tmp_path / "metrics.json"
    matrix_path = tmp_path / "matrix.json"
    artifact_path = tmp_path / "model.joblib"

    metrics = train_calibrated_svc(
        features_path=features_path,
        source_dataset_path=features_path,
        split_manifest_path=tmp_path / "split_manifest.json",
        artifact_path=artifact_path,
        metrics_path=metrics_path,
        confusion_matrix_path=matrix_path,
        n_splits=3,
        n_jobs=1,
    )

    assert metrics["rows"] == {"train": 45, "validation": 15, "test_used": 0}
    assert metrics["calibration"]["cv"] == "StratifiedKFold"
    assert metrics["validation"]["probability_sum_max_abs_error"] < 1e-12
    assert artifact_path.exists()
    assert matrix_path.exists()
    assert json.loads(metrics_path.read_text(encoding="utf-8"))["component_id"] == "D_CAL"
