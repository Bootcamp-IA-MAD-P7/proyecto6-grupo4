"""Selección y promoción operativa del Champion sin reevaluar el test protegido."""
from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

import joblib
import pandas as pd

from src.candidates.common import metric_summary
from src.data.historical_features import FEATURE_GENERATOR_VERSION, MODEL_FEATURES
from src.data.laliga_loader import TARGET_COLUMN, file_sha256
from src.evaluation.artifact_integrity import build_artifact_identity


COMPARABILITY_FIELDS = (
    "data_version_sha256",
    "features_sha256",
    "feature_generator_version",
    "split_manifest_reference",
)


def _read(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _select_champion(metrics_paths: list[str | Path]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Selecciona exclusivamente mediante evidencia de train y validation."""

    candidates = [_read(path) for path in metrics_paths]
    if not candidates:
        raise ValueError("Se requiere al menos un candidato.")
    reference = candidates[0]
    if any(
        any(candidate[key] != reference[key] for key in COMPARABILITY_FIELDS)
        for candidate in candidates
    ):
        raise ValueError("Los candidatos no son comparables: versiones o contratos distintos.")
    eligible = [
        candidate
        for candidate in candidates
        if candidate["overfitting_gap_macro_f1"] < 0.05
    ]
    if not eligible:
        raise ValueError("Ningún candidato cumple el umbral de overfitting.")
    champion = max(
        eligible,
        key=lambda item: (
            item["validation"]["macro_f1"],
            -item["inference_time_ms_per_row"],
        ),
    )
    comparability = {key: reference[key] for key in COMPARABILITY_FIELDS}
    return champion, comparability


def _load_development_rows(features_path: str | Path) -> pd.DataFrame:
    """Aísla train y validation; ninguna fila de test llega al estimador."""

    features = pd.read_csv(features_path)
    required = set(MODEL_FEATURES) | {TARGET_COLUMN, "split"}
    missing = sorted(required - set(features.columns))
    if missing:
        raise ValueError(f"Tabla de features inválida: faltan {missing}.")
    development = features.loc[
        features["split"].isin(["train", "validation"]),
        [*MODEL_FEATURES, TARGET_COLUMN, "split"],
    ].copy()
    if development.empty or set(development["split"]) != {"train", "validation"}:
        raise ValueError("Se requieren las particiones train y validation.")
    return development


def select_and_promote_champion(
    *,
    metrics_paths: list[str | Path],
    features_path: str | Path,
    source_dataset_path: str | Path,
    artifact_path: str | Path,
    metadata_path: str | Path,
    historical_test_metrics_path: str | Path,
) -> dict[str, Any]:
    """Promueve el Champion sin leer sus resultados ni reevaluar sobre test.

    La selección usa las métricas ya registradas de validation. Después, el
    estimador ganador se ajusta con train + validation para uso operativo. El
    test histórico queda congelado en un fichero separado y solo se referencia
    mediante su ruta y hash.
    """

    champion, comparability = _select_champion(metrics_paths)
    development = _load_development_rows(features_path)
    pipeline = joblib.load(champion["artifact_path"])
    started = perf_counter()
    pipeline.fit(
        development.loc[:, MODEL_FEATURES],
        development[TARGET_COLUMN],
    )
    fit_seconds = perf_counter() - started

    artifact = Path(artifact_path)
    artifact.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, artifact)
    artifact_identity = build_artifact_identity(artifact)

    historical_test = Path(historical_test_metrics_path)
    if not historical_test.is_file():
        raise FileNotFoundError(
            f"No existe la evidencia histórica de test: {historical_test}"
        )

    evidence = {
        "champion_candidate_id": champion["candidate_id"],
        "champion_model_version": champion["model_version"],
        "selection_rule": (
            "Mayor macro-F1 de validation entre candidatos con gap < 0.05; "
            "empate por menor latencia."
        ),
        "selection_timestamp_utc": datetime.now(UTC).isoformat(),
        "comparability": comparability,
        "validation": champion["validation"],
        "train": champion["train"],
        "overfitting_gap_macro_f1": champion["overfitting_gap_macro_f1"],
        "promotion_contract": {
            "fit_splits": ["train", "validation"],
            "fit_rows": len(development),
            "test_rows_used": 0,
            "test_metrics_recomputed": False,
        },
        "historical_test_evidence": {
            "status": "frozen_not_recomputed",
            "path": str(historical_test).replace("\\", "/"),
            "sha256": file_sha256(historical_test),
        },
        "final_fit_seconds": fit_seconds,
        "artifact_path": str(artifact).replace("\\", "/"),
        "feature_columns": list(MODEL_FEATURES),
        "feature_generator_version": FEATURE_GENERATOR_VERSION,
        "source_data_sha256": file_sha256(Path(source_dataset_path)),
        **artifact_identity,
        "limitations": (
            "Predicción orientativa; se apoya únicamente en histórico. "
            "Equipos nuevos usan cold-start y no se usan cuotas."
        ),
    }
    metadata = Path(metadata_path)
    metadata.parent.mkdir(parents=True, exist_ok=True)
    metadata.write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return evidence
