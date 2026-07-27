"""T-4.2: validación cruzada reproducible que nunca toca el test protegido.

Usa `TimeSeriesSplit` exclusivamente sobre las filas `split == "train"`,
ordenadas cronológicamente. Cada fold ajusta en una ventana creciente de
partidos pasados y mide en el bloque de partidos inmediatamente posterior,
igual que en producción: nunca se entrena con partidos futuros respecto al
bloque de medición. `validation` y `test` quedan completamente fuera de
este proceso.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pandas as pd
from sklearn.base import clone
from sklearn.model_selection import TimeSeriesSplit
from sklearn.pipeline import Pipeline

from src.candidates.common import CLASS_LABELS, metric_summary
from src.data.historical_features import FEATURE_GENERATOR_VERSION, MODEL_FEATURES
from src.data.laliga_loader import TARGET_COLUMN, file_sha256


def chronological_cv_scores(
    *,
    candidate_id: str,
    build_pipeline: Callable[[], Pipeline],
    features_path: str | Path,
    source_dataset_path: str | Path,
    n_splits: int = 4,
) -> dict[str, Any]:
    """Evalúa `build_pipeline()` con `TimeSeriesSplit` dentro de `train`.

    No usa `validation` ni `test`: es exclusivamente una estimación de la
    estabilidad de la configuración de hiperparámetros ya elegida, no un
    mecanismo de selección de Champion (eso sigue siendo T-2.6, sobre
    `validation`).
    """

    features = pd.read_csv(features_path, parse_dates=["match_date"])
    required = set(MODEL_FEATURES) | {TARGET_COLUMN, "split", "match_id", "match_date"}
    missing = sorted(required - set(features.columns))
    if missing:
        raise ValueError(f"Tabla de features inválida para CV: faltan {missing}.")
    train = (
        features.loc[features["split"].eq("train")]
        .sort_values(["match_date", "match_id"], kind="mergesort")
        .reset_index(drop=True)
    )
    if train.empty:
        raise ValueError("No hay filas de train para hacer validación cruzada.")

    splitter = TimeSeriesSplit(n_splits=n_splits)
    fold_scores: list[dict[str, Any]] = []
    for fold_index, (train_idx, test_idx) in enumerate(splitter.split(train)):
        cv_train, cv_test = train.iloc[train_idx], train.iloc[test_idx]
        if not set(CLASS_LABELS).issubset(set(cv_train[TARGET_COLUMN])):
            continue
        pipeline = clone(build_pipeline())
        pipeline.fit(cv_train.loc[:, MODEL_FEATURES], cv_train[TARGET_COLUMN])
        metrics, _ = metric_summary(pipeline, cv_test.loc[:, MODEL_FEATURES], cv_test[TARGET_COLUMN])
        fold_scores.append(
            {
                "fold": fold_index,
                "train_rows": int(len(cv_train)),
                "test_rows": int(len(cv_test)),
                "test_date_range": [
                    cv_test["match_date"].min().strftime("%Y-%m-%d"),
                    cv_test["match_date"].max().strftime("%Y-%m-%d"),
                ],
                **metrics,
            }
        )
    if not fold_scores:
        raise ValueError("Ningún fold contuvo las tres clases en train; reduce n_splits.")

    macro_f1_values = [fold["macro_f1"] for fold in fold_scores]
    mean_macro_f1 = sum(macro_f1_values) / len(macro_f1_values)
    variance = sum((value - mean_macro_f1) ** 2 for value in macro_f1_values) / len(macro_f1_values)
    summary = {
        "candidate_id": candidate_id,
        "method": "TimeSeriesSplit_within_train_only",
        "n_splits_requested": n_splits,
        "n_folds_scored": len(fold_scores),
        "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "data_version_sha256": file_sha256(Path(source_dataset_path)),
        "features_sha256": file_sha256(Path(features_path)),
        "folds": fold_scores,
        "macro_f1_mean": mean_macro_f1,
        "macro_f1_std": variance ** 0.5,
        "test_protection": "Solo usa filas split=train; validation y test nunca se leen aquí.",
    }
    return summary


def write_cv_summary(summary: dict[str, Any], path: str | Path) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
