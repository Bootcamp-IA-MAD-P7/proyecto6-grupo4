"""Entrena localmente el candidato A desde las features comunes."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.candidates.model_a.pipeline import train_candidate_a


if __name__ == "__main__":
    result = train_candidate_a(
        features_path="data/processed/laliga_historical_features_v1.csv",
        source_dataset_path="data/processed/laliga_matches_clean.csv",
        split_manifest_path="reports/metrics/split_manifest.json",
        artifact_path="models/candidates/model_a/candidate_a_logistic_regression_v1.joblib",
        metrics_path="reports/experiments/candidate_a_metrics.json",
        confusion_matrix_path="reports/experiments/candidate_a_validation_confusion_matrix.json",
        experiment_table_path="reports/experiments/experiments_table.csv",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
