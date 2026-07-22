"""CLI reproducible para preparar y analizar el dataset canónico de LaLiga."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.laliga_eda import run_full_eda
from src.data.laliga_loader import write_canonical_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--processed-path",
        type=Path,
        default=Path("data/processed/laliga_matches_eda.csv"),
    )
    parser.add_argument("--reports-dir", type=Path, default=Path("reports"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    canonical, manifest = write_canonical_outputs(
        raw_dir=args.raw_dir,
        processed_path=args.processed_path,
        manifest_path=args.reports_dir / "metrics" / "dataset_manifest.json",
    )
    metrics = run_full_eda(canonical, args.reports_dir)
    print(
        json.dumps(
            {
                "dataset_id": manifest["dataset_id"],
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
