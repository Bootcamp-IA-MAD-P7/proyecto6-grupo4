from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.candidates.ensemble import train_ensemble_abcd

print(train_ensemble_abcd(
    features_path="data/processed/laliga_historical_features_v1.csv",
    source_dataset_path="data/processed/laliga_matches_clean.csv",
    split_manifest_path="reports/metrics/split_manifest.json",
    artifact_path="models/ensemble/ensemble_abcd_soft_voting_v1.joblib",
    metrics_path="reports/experiments/ensemble_abcd_metrics.json",
    confusion_matrix_path="reports/experiments/ensemble_abcd_validation_confusion_matrix.json",
    experiment_table_path="reports/experiments/ensemble_table.csv",
))
