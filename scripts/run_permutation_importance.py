"""Interpretabilidad del Champion: permutation importance sobre validation.

Mide cuánto cae el macro-F1 del Champion cuando se baraja aleatoriamente
(permuta) cada feature por separado en el set de validation, sin tocar
train ni test. Es un cálculo real hecho contra el modelo vigente, no una
estimación manual: sustituye a los pesos ilustrativos que hasta ahora
mostraba el frontend.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import joblib
from sklearn.inspection import permutation_importance
from sklearn.metrics import make_scorer, f1_score

from src.data.historical_features import MODEL_FEATURES
from src.data.laliga_loader import TARGET_COLUMN, file_sha256

CHAMPION_ARTIFACT = "models/champion/laliga_champion_v1.joblib"
CHAMPION_METADATA = "reports/experiments/champion_metadata.json"
FEATURES_PATH = "data/processed/laliga_historical_features_v1.csv"
OUTPUT_PATH = "reports/experiments/champion_permutation_importance.json"
N_REPEATS = 10
SEED = 42

CLASS_LABELS = ["H", "D", "A"]
macro_f1_scorer = make_scorer(f1_score, labels=CLASS_LABELS, average="macro", zero_division=0)


def main() -> None:
    import pandas as pd

    metadata = json.loads(Path(CHAMPION_METADATA).read_text(encoding="utf-8"))
    features = pd.read_csv(FEATURES_PATH)
    validation = features.loc[features["split"].eq("validation"), [*MODEL_FEATURES, TARGET_COLUMN]].copy()
    x_val, y_val = validation.loc[:, MODEL_FEATURES], validation[TARGET_COLUMN]

    pipeline = joblib.load(CHAMPION_ARTIFACT)

    result = permutation_importance(
        pipeline, x_val, y_val,
        scoring=macro_f1_scorer,
        n_repeats=N_REPEATS,
        random_state=SEED,
        n_jobs=-1,
    )

    per_feature = sorted(
        (
            {
                "feature": feature,
                "importance_mean": float(mean),
                "importance_std": float(std),
            }
            for feature, mean, std in zip(MODEL_FEATURES, result.importances_mean, result.importances_std)
        ),
        key=lambda item: item["importance_mean"],
        reverse=True,
    )

    report = {
        "method": "sklearn.inspection.permutation_importance",
        "scoring": "macro_f1",
        "evaluated_on": "validation (never train ni test)",
        "n_repeats": N_REPEATS,
        "random_state": SEED,
        "champion_candidate_id": metadata["champion_candidate_id"],
        "champion_model_version": metadata["champion_model_version"],
        "artifact_sha256": metadata["artifact_sha256"],
        "data_version_sha256": file_sha256(Path(FEATURES_PATH.replace("laliga_historical_features_v1.csv", "laliga_matches_clean.csv"))),
        "baseline_macro_f1_validation": metadata["validation"]["macro_f1"],
        "per_feature_importance": per_feature,
    }
    Path(OUTPUT_PATH).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    for row in per_feature:
        print(f"{row['feature']:<32} importance_mean={row['importance_mean']:+.5f}  std={row['importance_std']:.5f}")


if __name__ == "__main__":
    main()
