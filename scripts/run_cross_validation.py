"""T-4.2: corre validación cruzada cronológica (solo train) para A, B, C y D
y registra la referencia en experiments_table.csv."""
from pathlib import Path
import csv
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.candidates.model_a.pipeline import build_pipeline_a
from src.candidates.model_b.pipeline import build_pipeline_b
from src.candidates.model_c.pipeline import build_pipeline_c
from src.candidates.model_d.pipeline import build_pipeline_d
from src.evaluation.cross_validation import chronological_cv_scores, write_cv_summary

FEATURES_PATH = "data/processed/laliga_historical_features_v1.csv"
SOURCE_PATH = "data/processed/laliga_matches_clean.csv"

BUILDERS = {
    "a": build_pipeline_a,
    "b": build_pipeline_b,
    "c": build_pipeline_c,
    "d": build_pipeline_d,
}


def _update_cv_reference(table_path: str, candidate_id: str, reference: str) -> None:
    path = Path(table_path)
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
        fieldnames = list(rows[0])
    for row in rows:
        if row["candidate_id"] == candidate_id:
            row["cv_summary_reference"] = reference
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


for name, builder in BUILDERS.items():
    candidate_id = name.upper()
    summary = chronological_cv_scores(
        candidate_id=candidate_id,
        build_pipeline=builder,
        features_path=FEATURES_PATH,
        source_dataset_path=SOURCE_PATH,
        n_splits=4,
    )
    reference = f"reports/experiments/candidate_{name}_cv_summary.json"
    write_cv_summary(summary, reference)
    _update_cv_reference("reports/experiments/experiments_table.csv", candidate_id, reference)
    print(candidate_id, "macro_f1_mean=", summary["macro_f1_mean"], "std=", summary["macro_f1_std"], "folds=", summary["n_folds_scored"])

print("CV completa.")
