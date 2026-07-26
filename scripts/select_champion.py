"""Selecciona el Champion y realiza la única evaluación final sobre test."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.evaluation.champion import select_and_evaluate_champion

print(select_and_evaluate_champion(
    metrics_paths=[f"reports/experiments/candidate_{name}_metrics.json" for name in "abcd"],
    features_path="data/processed/laliga_historical_features_v1.csv",
    source_dataset_path="data/processed/laliga_matches_clean.csv",
    artifact_path="models/champion/laliga_champion_v1.joblib",
    metadata_path="reports/experiments/champion_metadata.json",
    final_metrics_path="reports/experiments/champion_test_metrics.json",
))
