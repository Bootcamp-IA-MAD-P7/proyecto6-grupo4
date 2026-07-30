"""CLI reproducible para limpiar y combinar las dos fuentes raw de LaLiga."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data.laliga_loader import write_canonical_outputs


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument(
        "--processed-path",
        type=Path,
        default=Path("data/processed/laliga_matches_clean.csv"),
    )
    parser.add_argument("--metrics-dir", type=Path, default=Path("reports/metrics"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    canonical, manifest = write_canonical_outputs(
        raw_dir=args.raw_dir,
        processed_path=args.processed_path,
        manifest_path=args.metrics_dir / "dataset_manifest.json",
        preprocessing_report_path=args.metrics_dir / "preprocessing_summary.json",
        column_policy_path=args.metrics_dir / "source_column_policy.csv",
        provenance_path=args.metrics_dir / "source_provenance.json",
    )
    preprocessing = manifest["preprocessing"]
    print(
        json.dumps(
            {
                "dataset_id": manifest["dataset_id"],
                "processed_path": str(args.processed_path),
                "rows": int(len(canonical)),
                "columns": int(canonical.shape[1]),
                "overlap_rows": preprocessing["join"]["overlap_rows"],
                "duplicate_match_ids": preprocessing["output"]["duplicate_match_ids"],
                "missing_target": preprocessing["output"]["missing_target"],
                "sha256": preprocessing["output"]["sha256"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
