"""SVC RBF con calibración multiclase explícita para el ensemble."""

from __future__ import annotations

import json
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

from src.candidates.common import CLASS_LABELS, load_training_partitions
from src.data.historical_features import (
    FEATURE_GENERATOR_VERSION,
    MODEL_CATEGORICAL_FEATURES,
    MODEL_FEATURES,
    MODEL_NUMERIC_FEATURES,
)
from src.data.laliga_loader import TARGET_COLUMN, file_sha256


CALIBRATED_SVC_VERSION = "ensemble_svc_rbf_calibrated_v1"
CALIBRATED_SVC_SEED = 42
CALIBRATION_METHOD = "temperature"
CALIBRATION_SPLITS = 5


def build_base_svc_pipeline(seed: int = CALIBRATED_SVC_SEED) -> Pipeline:
    """Construye el SVC sin probabilidades internas y con preprocesamiento propio."""

    preprocessing = ColumnTransformer(
        [
            (
                "numeric",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="median")),
                        ("scaler", StandardScaler()),
                    ]
                ),
                list(MODEL_NUMERIC_FEATURES),
            ),
            (
                "teams",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                list(MODEL_CATEGORICAL_FEATURES),
            ),
        ]
    )
    classifier = SVC(
        kernel="rbf",
        C=0.5,
        gamma="scale",
        class_weight="balanced",
        random_state=seed,
    )
    return Pipeline(
        [
            ("preprocessing", preprocessing),
            ("classifier", classifier),
        ]
    )


def build_calibrated_svc(
    *,
    seed: int = CALIBRATED_SVC_SEED,
    n_splits: int = CALIBRATION_SPLITS,
    n_jobs: int | None = -1,
) -> CalibratedClassifierCV:
    """Calibra mediante predicciones fuera de fold generadas solo dentro de train."""

    if n_splits < 2:
        raise ValueError("La calibración cruzada requiere al menos dos splits.")
    return CalibratedClassifierCV(
        estimator=build_base_svc_pipeline(seed),
        method=CALIBRATION_METHOD,
        cv=StratifiedKFold(n_splits=n_splits, shuffle=False),
        n_jobs=n_jobs,
        ensemble=False,
    )


def _calibration_metrics(
    estimator: CalibratedClassifierCV,
    features: pd.DataFrame,
    target: pd.Series,
) -> tuple[dict[str, float], list[list[int]]]:
    probabilities = estimator.predict_proba(features)
    predictions = estimator.predict(features)
    classes = list(estimator.classes_)
    encoded_target = np.column_stack([target.eq(label).astype(float) for label in classes])
    confidence = probabilities.max(axis=1)
    correctness = predictions == target.to_numpy()
    expected_calibration_error = 0.0
    for lower, upper in zip(np.linspace(0.0, 1.0, 11)[:-1], np.linspace(0.0, 1.0, 11)[1:]):
        in_bin = (confidence > lower) & (confidence <= upper)
        if in_bin.any():
            expected_calibration_error += float(
                in_bin.mean() * abs(correctness[in_bin].mean() - confidence[in_bin].mean())
            )
    return {
        "macro_f1": float(
            f1_score(target, predictions, labels=CLASS_LABELS, average="macro", zero_division=0)
        ),
        "accuracy": float(accuracy_score(target, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(target, predictions)),
        "log_loss": float(log_loss(target, probabilities, labels=classes)),
        "multiclass_brier": float(np.mean(np.sum((probabilities - encoded_target) ** 2, axis=1))),
        "top_label_ece_10_bins": expected_calibration_error,
        "probability_sum_max_abs_error": float(
            np.max(np.abs(probabilities.sum(axis=1) - 1.0))
        ),
    }, confusion_matrix(target, predictions, labels=CLASS_LABELS).tolist()


def train_calibrated_svc(
    *,
    features_path: str | Path,
    source_dataset_path: str | Path,
    split_manifest_path: str | Path,
    artifact_path: str | Path,
    metrics_path: str | Path,
    confusion_matrix_path: str | Path,
    seed: int = CALIBRATED_SVC_SEED,
    n_splits: int = CALIBRATION_SPLITS,
    n_jobs: int | None = -1,
) -> dict[str, Any]:
    """Entrena en train y mide en validation sin consultar el test protegido."""

    train, validation = load_training_partitions(features_path)
    train = train.sort_values(["match_date", "match_id"], kind="mergesort")
    validation = validation.sort_values(["match_date", "match_id"], kind="mergesort")
    estimator = build_calibrated_svc(seed=seed, n_splits=n_splits, n_jobs=n_jobs)

    started = perf_counter()
    estimator.fit(train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    training_seconds = perf_counter() - started
    train_metrics, _ = _calibration_metrics(
        estimator,
        train.loc[:, MODEL_FEATURES],
        train[TARGET_COLUMN],
    )
    started = perf_counter()
    validation_metrics, matrix = _calibration_metrics(
        estimator,
        validation.loc[:, MODEL_FEATURES],
        validation[TARGET_COLUMN],
    )
    inference_ms = (perf_counter() - started) * 1000 / len(validation)
    gap = max(0.0, train_metrics["macro_f1"] - validation_metrics["macro_f1"])

    artifact = Path(artifact_path)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(estimator, artifact)
    metrics = {
        "component_id": "D_CAL",
        "member": "I4",
        "purpose": "probability_component_for_ensemble",
        "algorithm": "SVC RBF + explicit temperature calibration",
        "model_version": CALIBRATED_SVC_VERSION,
        "seed": seed,
        "calibration": {
            "method": CALIBRATION_METHOD,
            "cv": "StratifiedKFold",
            "n_splits": n_splits,
            "ensemble": False,
        },
        "base_svc": {
            "kernel": "rbf",
            "C": 0.5,
            "gamma": "scale",
            "probability": False,
            "class_weight": "balanced",
        },
        "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "data_version_sha256": file_sha256(Path(source_dataset_path)),
        "features_sha256": file_sha256(Path(features_path)),
        "split_manifest_reference": str(split_manifest_path).replace("\\", "/"),
        "feature_columns": list(MODEL_FEATURES),
        "rows": {
            "train": len(train),
            "validation": len(validation),
            "test_used": 0,
        },
        "train": train_metrics,
        "validation": validation_metrics,
        "overfitting_gap_macro_f1": gap,
        "training_time_seconds": training_seconds,
        "inference_time_ms_per_row": inference_ms,
        "artifact_path": str(artifact).replace("\\", "/"),
        "test_protection": "El calibrador recibe solo train; validation se usa para medir y test_used es 0.",
    }
    metrics_file = Path(metrics_path)
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    matrix_file = Path(confusion_matrix_path)
    matrix_file.parent.mkdir(parents=True, exist_ok=True)
    matrix_file.write_text(
        json.dumps({"labels": CLASS_LABELS, "matrix": matrix}, indent=2),
        encoding="utf-8",
    )
    return metrics
