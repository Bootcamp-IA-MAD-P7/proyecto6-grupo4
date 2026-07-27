"""Entrena el componente SVC RBF calibrado para el ensemble."""

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
