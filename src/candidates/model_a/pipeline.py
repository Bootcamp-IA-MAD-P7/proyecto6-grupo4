"""Entrenamiento reproducible del candidato A sin consultar el test protegido."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    log_loss,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.data.historical_features import (
    FEATURE_GENERATOR_VERSION,
    MODEL_CATEGORICAL_FEATURES,
    MODEL_FEATURES,
    MODEL_NUMERIC_FEATURES,
)
from src.data.laliga_loader import TARGET_COLUMN, file_sha256


MODEL_A_SEED = 42
MODEL_A_VERSION = "candidate_a_logistic_regression_v1"
CLASS_LABELS = ["H", "D", "A"]


def build_pipeline_a(seed: int = MODEL_A_SEED) -> Pipeline:
    """Construye el pipeline completo; imputación y escala se ajustan en train."""

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                list(MODEL_NUMERIC_FEATURES),
            ),
            (
                "teams",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                ]),
                list(MODEL_CATEGORICAL_FEATURES),
            ),
        ],
        remainder="drop",
    )
    return Pipeline([
        ("preprocessing", preprocessing),
        (
            "classifier",
            LogisticRegression(
                solver="lbfgs",
                l1_ratio=0.0,
                C=0.1,
                max_iter=2000,
                class_weight="balanced",
                random_state=seed,
            ),
        ),
    ])


def _metric_summary(pipeline: Pipeline, x: pd.DataFrame, y: pd.Series) -> tuple[dict[str, float], np.ndarray]:
    probabilities = pipeline.predict_proba(x)
    predictions = pipeline.predict(x)
    return {
        "macro_f1": float(f1_score(y, predictions, labels=CLASS_LABELS, average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(y, predictions)),
        "balanced_accuracy": float(balanced_accuracy_score(y, predictions)),
        "log_loss": float(log_loss(y, probabilities, labels=pipeline.classes_)),
    }, confusion_matrix(y, predictions, labels=CLASS_LABELS)


def _load_feature_table(path: str | Path) -> pd.DataFrame:
    features = pd.read_csv(path, parse_dates=["match_date"])
    required = set(MODEL_FEATURES) | {TARGET_COLUMN, "split", "match_id"}
    missing = sorted(required - set(features.columns))
    if missing:
        raise ValueError(f"La tabla de features no cumple el contrato de Pipeline A: {missing}")
    if features["match_id"].duplicated().any() or not set(features["split"].dropna()).issubset({"train", "validation", "test"}):
        raise ValueError("La tabla de features contiene ids o etiquetas de split inválidos.")
    return features


def _upsert_experiment_row(path: str | Path, row: dict[str, str]) -> None:
    table_path = Path(path)
    with table_path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fieldnames = list(rows[0]) if rows else list(row)
    if set(fieldnames) != set(row):
        raise ValueError("El contrato de reports/experiments/experiments_table.csv ha cambiado.")
    replaced = False
    for existing in rows:
        if existing["candidate_id"] == "A":
            existing.update(row)
            replaced = True
    if not replaced:
        rows.append(row)
    with table_path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def train_candidate_a(
    features_path: str | Path,
    source_dataset_path: str | Path,
    split_manifest_path: str | Path,
    artifact_path: str | Path,
    metrics_path: str | Path,
    confusion_matrix_path: str | Path,
    experiment_table_path: str | Path,
    *,
    seed: int = MODEL_A_SEED,
) -> dict[str, Any]:
    """Entrena en train y evalúa en validation; el test nunca llega al estimador."""

    features = _load_feature_table(features_path)
    train = features.loc[features["split"].eq("train")].copy()
    validation = features.loc[features["split"].eq("validation")].copy()
    if train.empty or validation.empty:
        raise ValueError("Pipeline A necesita filas train y validation no vacías.")
    if not set(CLASS_LABELS).issubset(set(train[TARGET_COLUMN])):
        raise ValueError("Train debe contener las tres clases H, D y A.")

    pipeline = build_pipeline_a(seed)
    started_at = perf_counter()
    pipeline.fit(train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    training_time_seconds = perf_counter() - started_at
    train_metrics, _ = _metric_summary(pipeline, train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    validation_started_at = perf_counter()
    validation_metrics, validation_cm = _metric_summary(
        pipeline, validation.loc[:, MODEL_FEATURES], validation[TARGET_COLUMN]
    )
    inference_time_ms = ((perf_counter() - validation_started_at) / len(validation)) * 1000.0
    gap = max(0.0, train_metrics["macro_f1"] - validation_metrics["macro_f1"])

    artifact = Path(artifact_path)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact)
    metrics = {
        "candidate_id": "A",
        "member": "I1",
        "model_version": MODEL_A_VERSION,
        "algorithm": "multinomial_logistic_regression",
        "seed": seed,
        "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "data_version_sha256": file_sha256(Path(source_dataset_path)),
        "split_manifest_reference": str(split_manifest_path).replace("\\", "/"),
        "features_sha256": file_sha256(Path(features_path)),
        "feature_columns": list(MODEL_FEATURES),
        "rows": {"train": int(len(train)), "validation": int(len(validation)), "test_used": 0},
        "hyperparameters": {
            key: value
            for key, value in pipeline.named_steps["classifier"].get_params().items()
            if key != "penalty"
        },
        "train": train_metrics,
        "validation": validation_metrics,
        "overfitting_gap_macro_f1": gap,
        "absolute_macro_f1_difference": abs(train_metrics["macro_f1"] - validation_metrics["macro_f1"]),
        "training_time_seconds": training_time_seconds,
        "inference_time_ms_per_row": inference_time_ms,
        "artifact_path": str(artifact).replace("\\", "/"),
        "test_protection": "Las filas split=test no se usan para ajuste, entrenamiento, validación ni selección.",
    }
    metrics_file = Path(metrics_path)
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    matrix_file = Path(confusion_matrix_path)
    matrix_file.parent.mkdir(parents=True, exist_ok=True)
    matrix_file.write_text(
        json.dumps({"labels": CLASS_LABELS, "matrix": validation_cm.tolist()}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _upsert_experiment_row(
        experiment_table_path,
        {
            "candidate_id": "A",
            "member": "I1",
            "algorithm": "Regresión logística multinomial",
            "data_version_sha256": metrics["data_version_sha256"],
            "split_manifest_reference": metrics["split_manifest_reference"],
            "features_version": f"{FEATURE_GENERATOR_VERSION}:{metrics['features_sha256']}",
            "transformations_summary": "Imputación mediana + StandardScaler numéricos; moda + OneHot equipos; ajustado solo en train.",
            "hyperparameters": json.dumps(metrics["hyperparameters"], sort_keys=True),
            "seed": str(seed),
            "train_macro_f1": f"{train_metrics['macro_f1']:.6f}",
            "validation_macro_f1": f"{validation_metrics['macro_f1']:.6f}",
            "overfitting_gap_macro_f1": f"{gap:.6f}",
            "train_accuracy": f"{train_metrics['accuracy']:.6f}",
            "validation_accuracy": f"{validation_metrics['accuracy']:.6f}",
            "validation_balanced_accuracy": f"{validation_metrics['balanced_accuracy']:.6f}",
            "validation_log_loss": f"{validation_metrics['log_loss']:.6f}",
            "cv_summary_reference": "not_applied_temporal_holdout_only",
            "confusion_matrix_reference": str(matrix_file).replace("\\", "/"),
            "training_time_seconds": f"{training_time_seconds:.6f}",
            "inference_time_ms": f"{inference_time_ms:.6f}",
            "artifact_path": str(artifact).replace("\\", "/"),
            "evidence_path": str(metrics_file).replace("\\", "/"),
            "limitations_and_errors": "No usa cuotas; la primera aparición de equipos usa valores cold-start; test reservado.",
            "status": "ready_for_comparison" if gap < 0.05 else "disqualified",
        },
    )
    return metrics
