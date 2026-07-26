"""Regenera localmente la tabla común de features prepartido."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.historical_features import FEATURE_OUTPUT_FILENAME, generate_historical_features


if __name__ == "__main__":
    _, manifest = generate_historical_features(
        processed_path="data/processed/laliga_matches_clean.csv",
        splits_path="data/processed/splits/laliga_splits.csv",
        features_output_path=f"data/processed/{FEATURE_OUTPUT_FILENAME}",
        manifest_output_path="reports/metrics/historical_features_manifest.json",
    )
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
