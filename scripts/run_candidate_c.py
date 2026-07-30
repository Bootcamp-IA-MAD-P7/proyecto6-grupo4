from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.candidates.model_c.pipeline import train_candidate_c
print(train_candidate_c(features_path="data/processed/laliga_historical_features_v1.csv", source_dataset_path="data/processed/laliga_matches_clean.csv", split_manifest_path="reports/metrics/split_manifest.json", artifact_path="models/candidates/model_c/candidate_c_random_forest_v1.joblib", metrics_path="reports/experiments/candidate_c_metrics.json", confusion_matrix_path="reports/experiments/candidate_c_validation_confusion_matrix.json", experiment_table_path="reports/experiments/experiments_table.csv"))
