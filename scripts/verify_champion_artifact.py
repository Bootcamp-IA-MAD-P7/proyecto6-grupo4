"""Comprueba que el Champion local coincide con la metadata versionada."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.evaluation.artifact_integrity import verify_champion_artifact


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--artifact",
        default="models/champion/laliga_champion_v1.joblib",
    )
    parser.add_argument(
        "--metadata",
        default="reports/experiments/champion_metadata.json",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = verify_champion_artifact(args.artifact, args.metadata)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
