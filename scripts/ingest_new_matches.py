"""T-4.4: valida un CSV de partidos nuevos (esquema raw football-data) y los
deja en staging, sin tocar el dataset de entrenamiento.

Uso: ./.venv/Scripts/python.exe scripts/ingest_new_matches.py <csv_nuevo>
"""
from pathlib import Path
import sys
import json

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.data.ingestion import stage_new_matches, validate_new_matches

if len(sys.argv) != 2:
    raise SystemExit("Uso: run_ingest_new_matches.py <ruta_csv_nuevo>")

new_raw = pd.read_csv(sys.argv[1])
staged, report = validate_new_matches(new_raw, "data/processed/laliga_matches_clean.csv")
written = stage_new_matches(staged, "data/processed/staging/pending_matches.csv")
print(json.dumps(report, ensure_ascii=False, indent=2))
print(f"Filas escritas en staging: {written}")
