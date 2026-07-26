"""Selección gobernada del Champion y evaluación final única sobre test."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib
import pandas as pd

from src.candidates.common import CLASS_LABELS, metric_summary
from src.data.historical_features import FEATURE_GENERATOR_VERSION, MODEL_FEATURES
from src.data.laliga_loader import TARGET_COLUMN, file_sha256


def _read(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def select_and_evaluate_champion(
    *, metrics_paths: list[str | Path], features_path: str | Path, source_dataset_path: str | Path,
    artifact_path: str | Path, metadata_path: str | Path, final_metrics_path: str | Path,
) -> dict[str, Any]:
    """Escoge por validation y, solo después, evalúa una vez el test protegido."""

    candidates = [_read(path) for path in metrics_paths]
    reference = candidates[0]
    required = ("data_version_sha256", "features_sha256", "feature_generator_version", "split_manifest_reference")
    if any(any(candidate[key] != reference[key] for key in required) for candidate in candidates):
        raise ValueError("Los candidatos no son comparables: versiones o contratos distintos.")
    eligible = [candidate for candidate in candidates if candidate["overfitting_gap_macro_f1"] < .05]
    if not eligible:
        raise ValueError("Ningún candidato cumple el umbral de overfitting.")
    champion = max(eligible, key=lambda item: (item["validation"]["macro_f1"], -item["inference_time_ms_per_row"]))
    features = pd.read_csv(features_path)
    development = features.loc[features["split"].isin(["train", "validation"])].copy()
    test = features.loc[features["split"].eq("test")].copy()
    if test.empty or development.empty:
        raise ValueError("No existen las particiones requeridas para la evaluación final.")
    pipeline = joblib.load(champion["artifact_path"])
    started = perf_counter()
    pipeline.fit(development.loc[:, MODEL_FEATURES], development[TARGET_COLUMN])
    fit_seconds = perf_counter() - started
    test_metrics, test_matrix = metric_summary(pipeline, test.loc[:, MODEL_FEATURES], test[TARGET_COLUMN])
    artifact = Path(artifact_path)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact)
    evidence = {
        "champion_candidate_id": champion["candidate_id"], "champion_model_version": champion["model_version"],
        "selection_rule": "Mayor macro-F1 de validation entre candidatos con gap < 0.05; empate por menor latencia.",
        "selection_timestamp_utc": datetime.now(UTC).isoformat(),
        "comparability": {key: reference[key] for key in required},
        "validation": champion["validation"], "train": champion["train"],
        "overfitting_gap_macro_f1": champion["overfitting_gap_macro_f1"],
        "final_fit_rows": len(development), "test_rows": len(test), "test_used_once": True,
        "test": test_metrics, "test_confusion_matrix": {"labels": CLASS_LABELS, "matrix": test_matrix},
        "final_fit_seconds": fit_seconds, "artifact_path": str(artifact).replace("\\", "/"),
        "feature_columns": list(MODEL_FEATURES), "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "source_data_sha256": file_sha256(Path(source_dataset_path)),
        "limitations": "Predicción orientativa; se apoya únicamente en histórico. Equipos nuevos usan cold-start y no se usan cuotas.",
    }
    Path(metadata_path).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    Path(final_metrics_path).write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    return evidence
