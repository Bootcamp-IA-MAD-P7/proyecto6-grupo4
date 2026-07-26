from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.candidates.model_b.pipeline import train_candidate_b
print(train_candidate_b(features_path="data/processed/laliga_historical_features_v1.csv", source_dataset_path="data/processed/laliga_matches_clean.csv", split_manifest_path="reports/metrics/split_manifest.json", artifact_path="models/candidates/model_b/candidate_b_hist_gradient_boosting_v1.joblib", metrics_path="reports/experiments/candidate_b_metrics.json", confusion_matrix_path="reports/experiments/candidate_b_validation_confusion_matrix.json", experiment_table_path="reports/experiments/experiments_table.csv"))
