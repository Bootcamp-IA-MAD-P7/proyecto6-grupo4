"""Diagnóstico de calidad de calibración del SVC RBF (histórico, no productivo).

Este script NO forma parte del flujo vigente de entrenamiento. El SVC
calibrado que realmente se usa en el candidato D y en el Champion
ENSEMBLE_ABCD se entrena vía `scripts/run_candidate_d.py`, que reutiliza el
mismo `build_calibrated_svc` de `src/ensemble/svc_calibrated.py`.

Este script se conserva únicamente para volver a calcular las métricas
específicas de calibración (Brier multiclase, ECE por bins,
error de suma de probabilidades) que `train_candidate_d` no reporta. El
artefacto y las métricas que genera (`models/ensemble/ensemble_svc_rbf_calibrated_v1.joblib`,
`reports/experiments/ensemble_svc_calibrated_metrics.json`) son solo un
componente de diagnóstico: ningún script de producción los lee.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ensemble.svc_calibrated import train_calibrated_svc


if __name__ == "__main__":
    result = train_calibrated_svc(
        features_path="data/processed/laliga_historical_features_v1.csv",
        source_dataset_path="data/processed/laliga_matches_clean.csv",
        split_manifest_path="reports/metrics/split_manifest.json",
        artifact_path="models/ensemble/ensemble_svc_rbf_calibrated_v1.joblib",
        metrics_path="reports/experiments/ensemble_svc_calibrated_metrics.json",
        confusion_matrix_path=(
            "reports/experiments/ensemble_svc_calibrated_validation_confusion_matrix.json"
        ),
    )
    print(
        json.dumps(
            {
                "model_version": result["model_version"],
                "rows": result["rows"],
                "validation": result["validation"],
                "overfitting_gap_macro_f1": result["overfitting_gap_macro_f1"],
                "artifact_path": result["artifact_path"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
