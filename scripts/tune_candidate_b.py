"""Búsqueda reproducible de hiperparámetros para el candidato B (T-4.2).

Reproduce, con código versionado, la búsqueda de 256 combinaciones que
`reports/experiments/ensemble_abcd_review.md` describía sin script asociado.
Ajusta cada combinación solo en `train` y la puntúa en `validation`, sin
tocar nunca `test` (mismo contrato que el resto de candidatos). Los
hiperparámetros no buscados (`max_iter`, `class_weight`, `early_stopping`,
`validation_fraction`, `n_iter_no_change`) se mantienen fijos, igual que en
`src/candidates/model_b/pipeline.py`.
"""

from __future__ import annotations

import json
import sys
from itertools import product
from pathlib import Path
from time import perf_counter

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder

from src.candidates.common import load_training_partitions, metric_summary
from src.candidates.model_b.pipeline import MODEL_B_SEED
from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES
from src.data.laliga_loader import TARGET_COLUMN, file_sha256

FEATURES_PATH = "data/processed/laliga_historical_features_v1.csv"
SOURCE_PATH = "data/processed/laliga_matches_clean.csv"
OUTPUT_PATH = "reports/experiments/candidate_b_tuning_search.json"

GRID = {
    "learning_rate": [0.01, 0.025, 0.05, 0.1],
    "max_leaf_nodes": [15, 19, 23, 31],
    "min_samples_leaf": [10, 20, 30, 40],
    "l2_regularization": [0.0, 0.5, 1.0, 2.0],
}


def build_pipeline(**hyperparams) -> Pipeline:
    pre = ColumnTransformer([
        ("numeric", SimpleImputer(strategy="median"), list(MODEL_NUMERIC_FEATURES)),
        ("teams", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
        ]), list(MODEL_CATEGORICAL_FEATURES)),
    ])
    classifier = HistGradientBoostingClassifier(
        max_iter=300,
        class_weight="balanced",
        early_stopping=True,
        validation_fraction=0.15,
        n_iter_no_change=15,
        random_state=MODEL_B_SEED,
        **hyperparams,
    )
    return Pipeline([("preprocessing", pre), ("classifier", classifier)])


def main() -> None:
    train, validation = load_training_partitions(FEATURES_PATH)
    x_train, y_train = train.loc[:, list(MODEL_CATEGORICAL_FEATURES) + list(MODEL_NUMERIC_FEATURES)], train[TARGET_COLUMN]
    x_val, y_val = validation.loc[:, list(MODEL_CATEGORICAL_FEATURES) + list(MODEL_NUMERIC_FEATURES)], validation[TARGET_COLUMN]

    combos = list(product(*GRID.values()))
    keys = list(GRID.keys())
    results = []
    started_all = perf_counter()
    for index, values in enumerate(combos, start=1):
        params = dict(zip(keys, values))
        pipeline = build_pipeline(**params)
        started = perf_counter()
        pipeline.fit(x_train, y_train)
        train_metrics, _ = metric_summary(pipeline, x_train, y_train)
        validation_metrics, _ = metric_summary(pipeline, x_val, y_val)
        elapsed = perf_counter() - started
        gap = max(0.0, train_metrics["macro_f1"] - validation_metrics["macro_f1"])
        results.append({
            "params": params,
            "train_macro_f1": train_metrics["macro_f1"],
            "validation_macro_f1": validation_metrics["macro_f1"],
            "overfitting_gap_macro_f1": gap,
            "fit_seconds": elapsed,
        })
        print(f"[{index}/{len(combos)}] {params} -> val_macro_f1={validation_metrics['macro_f1']:.6f} gap={gap:.6f}")

    best = max(results, key=lambda item: item["validation_macro_f1"])
    deployed_params = {"learning_rate": 0.025, "max_leaf_nodes": 19, "min_samples_leaf": 20, "l2_regularization": 0.5}
    deployed_result = next(r for r in results if r["params"] == deployed_params)

    report = {
        "candidate_id": "B",
        "search_strategy": "grid_search_manual_train_fit_validation_score",
        "search_space": GRID,
        "n_combinations": len(combos),
        "fixed_hyperparameters": {
            "max_iter": 300, "class_weight": "balanced", "early_stopping": True,
            "validation_fraction": 0.15, "n_iter_no_change": 15, "random_state": MODEL_B_SEED,
        },
        "data_version_sha256": file_sha256(Path(SOURCE_PATH)),
        "features_sha256": file_sha256(Path(FEATURES_PATH)),
        "total_search_seconds": perf_counter() - started_all,
        "best_result": best,
        "deployed_pipeline_result": {
            "params": deployed_params,
            **{k: v for k, v in deployed_result.items() if k != "params"},
            "matches_best_of_grid": deployed_result["params"] == best["params"],
        },
        "all_results": results,
    }
    Path(OUTPUT_PATH).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\nMejor combinación:", best["params"], "val_macro_f1=", best["validation_macro_f1"])
    print("Configuración desplegada (src/candidates/model_b/pipeline.py):", deployed_params, "val_macro_f1=", deployed_result["validation_macro_f1"])
    print("¿La desplegada es la mejor de la malla?:", deployed_result["params"] == best["params"])


if __name__ == "__main__":
    main()
