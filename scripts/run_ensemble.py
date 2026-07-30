"""[HISTÓRICO T-4.1] Entrena el ensemble A+D original.

No es el flujo vigente: el Champion actual es ENSEMBLE_ABCD, generado por
`scripts/run_ensemble_abcd.py` + `scripts/select_champion.py`. Este script se
conserva por trazabilidad de T-4.1, cuando B y C aún no calificaban.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.candidates.ensemble import train_ensemble

print(train_ensemble(
    features_path="data/processed/laliga_historical_features_v1.csv",
    source_dataset_path="data/processed/laliga_matches_clean.csv",
    split_manifest_path="reports/metrics/split_manifest.json",
    artifact_path="models/ensemble/ensemble_ad_soft_voting_v1.joblib",
    metrics_path="reports/experiments/ensemble_metrics.json",
    confusion_matrix_path="reports/experiments/ensemble_validation_confusion_matrix.json",
    experiment_table_path="reports/experiments/ensemble_table.csv",
))
