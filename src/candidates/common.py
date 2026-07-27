"""Contrato reutilizable para los candidatos B, C y D.

El módulo centraliza la carga, la separación temporal y la evidencia para que
ningún candidato pueda cambiar accidentalmente datos, métricas o el test.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib
import pandas as pd
from sklearn.metrics import accuracy_score, balanced_accuracy_score, confusion_matrix, f1_score, log_loss

from src.data.historical_features import FEATURE_GENERATOR_VERSION, MODEL_FEATURES
from src.data.laliga_loader import TARGET_COLUMN, file_sha256


CLASS_LABELS = ["H", "D", "A"]


def load_training_partitions(path: str | Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Carga solo los subconjuntos admitidos por el contrato de candidatos."""

    features = pd.read_csv(path)
    required = set(MODEL_FEATURES) | {TARGET_COLUMN, "split", "match_id"}
    missing = sorted(required - set(features.columns))
    if missing or features["match_id"].duplicated().any():
        raise ValueError(f"Tabla de features inválida: faltan {missing} o hay IDs duplicados.")
    train = features.loc[features["split"].eq("train")].copy()
    validation = features.loc[features["split"].eq("validation")].copy()
    if train.empty or validation.empty or not set(CLASS_LABELS).issubset(train[TARGET_COLUMN]):
        raise ValueError("Se requieren train y validation con las tres clases.")
    return train, validation


def metric_summary(pipeline: Any, x: pd.DataFrame, y: pd.Series) -> tuple[dict[str, float], list[list[int]]]:
    probabilities = pipeline.predict_proba(x)
    prediction = pipeline.predict(x)
    return {
        "macro_f1": float(f1_score(y, prediction, labels=CLASS_LABELS, average="macro", zero_division=0)),
        "accuracy": float(accuracy_score(y, prediction)),
        "balanced_accuracy": float(balanced_accuracy_score(y, prediction)),
        "log_loss": float(log_loss(y, probabilities, labels=pipeline.classes_)),
    }, confusion_matrix(y, prediction, labels=CLASS_LABELS).tolist()


def upsert_experiment(path: str | Path, row: dict[str, str]) -> None:
    table = Path(path)
    with table.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fields = list(rows[0]) if rows else list(row)
    if set(fields) != set(row):
        raise ValueError("El contrato de la tabla de experimentos ha cambiado.")
    for existing in rows:
        if existing["candidate_id"] == row["candidate_id"]:
            existing.update(row)
            break
    else:
        rows.append(row)
    with table.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def train_candidate(
    *,
    candidate_id: str,
    member: str,
    algorithm: str,
    model_version: str,
    pipeline: Any,
    features_path: str | Path,
    source_dataset_path: str | Path,
    split_manifest_path: str | Path,
    artifact_path: str | Path,
    metrics_path: str | Path,
    confusion_matrix_path: str | Path,
    experiment_table_path: str | Path,
    seed: int,
    transformations_summary: str,
    limitations: str,
) -> dict[str, Any]:
    """Ajusta en train, mide en validation y registra evidencia comparable."""

    train, validation = load_training_partitions(features_path)
    started = perf_counter()
    pipeline.fit(train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    training_seconds = perf_counter() - started
    train_metrics, _ = metric_summary(pipeline, train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    started = perf_counter()
    validation_metrics, matrix = metric_summary(pipeline, validation.loc[:, MODEL_FEATURES], validation[TARGET_COLUMN])
    inference_ms = (perf_counter() - started) * 1000 / len(validation)
    gap = max(0.0, train_metrics["macro_f1"] - validation_metrics["macro_f1"])

    artifact = Path(artifact_path)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact)
    metrics = {
        "candidate_id": candidate_id, "member": member, "algorithm": algorithm,
        "model_version": model_version, "seed": seed,
        "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "data_version_sha256": file_sha256(Path(source_dataset_path)),
        "split_manifest_reference": str(split_manifest_path).replace("\\", "/"),
        "features_sha256": file_sha256(Path(features_path)),
        "feature_columns": list(MODEL_FEATURES),
        "rows": {"train": len(train), "validation": len(validation), "test_used": 0},
        "hyperparameters": pipeline.named_steps["classifier"].get_params(),
        "train": train_metrics, "validation": validation_metrics,
        "overfitting_gap_macro_f1": gap,
        "absolute_macro_f1_difference": abs(train_metrics["macro_f1"] - validation_metrics["macro_f1"]),
        "training_time_seconds": training_seconds, "inference_time_ms_per_row": inference_ms,
        "artifact_path": str(artifact).replace("\\", "/"),
        "test_protection": "El estimador recibe únicamente train y validation; test_used es siempre 0.",
    }
    metrics_file = Path(metrics_path)
    metrics_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_file.write_text(json.dumps(metrics, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    matrix_file = Path(confusion_matrix_path)
    matrix_file.write_text(json.dumps({"labels": CLASS_LABELS, "matrix": matrix}, indent=2), encoding="utf-8")
    upsert_experiment(experiment_table_path, {
        "candidate_id": candidate_id, "member": member, "algorithm": algorithm,
        "data_version_sha256": metrics["data_version_sha256"],
        "split_manifest_reference": metrics["split_manifest_reference"],
        "features_version": f"{FEATURE_GENERATOR_VERSION}:{metrics['features_sha256']}",
        "transformations_summary": transformations_summary,
        "hyperparameters": json.dumps(metrics["hyperparameters"], sort_keys=True, default=str), "seed": str(seed),
        "train_macro_f1": f"{train_metrics['macro_f1']:.6f}", "validation_macro_f1": f"{validation_metrics['macro_f1']:.6f}",
        "overfitting_gap_macro_f1": f"{gap:.6f}", "train_accuracy": f"{train_metrics['accuracy']:.6f}",
        "validation_accuracy": f"{validation_metrics['accuracy']:.6f}",
        "validation_balanced_accuracy": f"{validation_metrics['balanced_accuracy']:.6f}",
        "validation_log_loss": f"{validation_metrics['log_loss']:.6f}", "cv_summary_reference": "not_applied_temporal_holdout_only",
        "confusion_matrix_reference": str(matrix_file).replace("\\", "/"),
        "training_time_seconds": f"{training_seconds:.6f}", "inference_time_ms": f"{inference_ms:.6f}",
        "artifact_path": str(artifact).replace("\\", "/"), "evidence_path": str(metrics_file).replace("\\", "/"),
        "limitations_and_errors": limitations, "status": "ready_for_comparison" if gap < .05 else "disqualified",
    })
    return metrics
