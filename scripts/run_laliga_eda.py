"""CLI reproducible para analizar el dataset limpio de LaLiga."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.laliga_eda import run_full_eda
from src.data.laliga_loader import load_processed_dataset
from src.evaluation.splits import TEST_SEASONS, assign_splits


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--processed-path",
        type=Path,
        default=Path("data/processed/laliga_matches_clean.csv"),
    )
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    canonical = load_processed_dataset(args.processed_path)
    development = canonical.loc[assign_splits(canonical).ne("test")].copy()
    metrics = run_full_eda(development, args.reports_dir)
    scope = {
        "scope": "development_only_train_and_validation",
        "excluded_test_seasons": TEST_SEASONS,
        "source_rows": int(len(canonical)),
        "analyzed_rows": int(len(development)),
    }
    metrics_dir = args.reports_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    (metrics_dir / "eda_scope.json").write_text(
        json.dumps(scope, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "dataset_id": "laliga_matches_1995_96_to_2025_26_v1",
                "processed_path": str(args.processed_path),
                "rows": metrics["quality"]["rows"],
                "columns": metrics["quality"]["columns"],
                "scope": scope["scope"],
                "report": str(args.reports_dir / "laliga_eda.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
