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
    metrics = run_full_eda(canonical, args.reports_dir)
    print(
        json.dumps(
            {
                "dataset_id": "laliga_matches_1995_96_to_2025_26_v1",
                "processed_path": str(args.processed_path),
                "rows": metrics["quality"]["rows"],
                "columns": metrics["quality"]["columns"],
                "report": str(args.reports_dir / "laliga_eda.md"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
