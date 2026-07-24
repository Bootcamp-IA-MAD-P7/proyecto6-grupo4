"""Particiones comunes congeladas de entrenamiento, validación y test (T-1.5).

Implementa el protocolo aprobado en ``docs/decisions/0002-evaluation-protocol-proposal.md``:
partición cronológica por temporada (no aleatoria) para evitar fuga temporal, con
el test final reservado a un único uso posterior a la selección del Champion.

La asignación temporada -> partición queda fijada como constante. Si el dataset
canónico incorpora una temporada no contemplada aquí, la función falla en vez de
reasignar particiones en silencio: un cambio de cobertura temporal exige una
decisión explícita del equipo, no un recálculo automático.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.data.laliga_loader import file_sha256, load_processed_dataset

SPLIT_SEED = 42
PROTOCOL_REFERENCE = "docs/decisions/0002-evaluation-protocol-proposal.md"

TRAIN_SEASONS = [
    "1995-96", "1996-97", "1997-98", "1998-99", "1999-00",
    "2000-01", "2001-02", "2002-03", "2003-04", "2004-05",
    "2005-06", "2006-07", "2007-08", "2008-09", "2009-10",
    "2010-11", "2011-12", "2012-13", "2013-14", "2014-15",
    "2015-16", "2016-17", "2017-18", "2018-19", "2019-20",
]
VALIDATION_SEASONS = ["2020-21", "2021-22", "2022-23"]
TEST_SEASONS = ["2023-24", "2024-25", "2025-26"]

FROZEN_SEASON_SPLIT: dict[str, str] = {
    **{season: "train" for season in TRAIN_SEASONS},
    **{season: "validation" for season in VALIDATION_SEASONS},
    **{season: "test" for season in TEST_SEASONS},
}


def assign_splits(frame: pd.DataFrame) -> pd.Series:
    """Devuelve la etiqueta de partición (train/validation/test) por fila.

    Lanza ``ValueError`` si aparece una temporada fuera del mapeo congelado,
    en vez de asignarla implícitamente.
    """

    unknown_seasons = sorted(set(frame["season"].dropna()) - set(FROZEN_SEASON_SPLIT))
    if unknown_seasons:
        raise ValueError(
            "Temporadas no contempladas en la partición congelada: "
            f"{unknown_seasons}. Re-congelar requiere decisión explícita del equipo."
        )
    return frame["season"].map(FROZEN_SEASON_SPLIT).astype("string")


def split_row_counts(frame: pd.DataFrame) -> dict[str, int]:
    splits = assign_splits(frame)
    return {
        label: int((splits == label).sum())
        for label in ("train", "validation", "test")
    }


def build_split_manifest(
    processed_path: str | Path,
    frame: pd.DataFrame,
) -> dict[str, Any]:
    counts = split_row_counts(frame)
    total = sum(counts.values())
    return {
        "protocol_reference": PROTOCOL_REFERENCE,
        "status": "frozen_team_ratified_2026-07-24",
        "frozen_at": "2026-07-23",
        "responsible": ["I1", "I2"],
        "technical_approvals": {
            "I1": {
                "status": "approved",
                "date": "2026-07-23",
                "scope": "dataset_hash_season_assignment_counts_reproducibility_test_protection",
            },
            "I3_I4": {
                "status": "cross_review_ratified",
                "date": "2026-07-24",
                "scope": "season_assignment_counts_reproducibility_test_protection",
            },
        },
        "required_cross_reviewers_pending": [],
        "seed": SPLIT_SEED,
        "strategy": "chronological_by_season_no_shuffle_no_stratification",
        "rationale": (
            "El EDA detecta deriva temporal en la tasa de victoria local entre "
            "temporadas; una partición aleatoria filtraria informacion futura "
            "hacia el entrenamiento."
        ),
        "source_dataset": {
            "path": str(processed_path),
            "sha256": file_sha256(Path(processed_path)),
            "rows": int(len(frame)),
        },
        "season_assignment": {
            "train": TRAIN_SEASONS,
            "validation": VALIDATION_SEASONS,
            "test": TEST_SEASONS,
        },
        "row_counts": counts,
        "row_fractions": {
            label: round(count / total, 4) for label, count in counts.items()
        },
        "test_protection": (
            "El split de test no se utiliza para EDA, tuning ni comparacion de "
            "candidatos. Se evalua una unica vez tras seleccionar el Champion (T-2.6)."
        ),
    }


def freeze_splits(
    processed_path: str | Path,
    splits_output_path: str | Path,
    manifest_output_path: str | Path,
) -> dict[str, Any]:
    """Genera y persiste la partición congelada a partir del dataset canónico."""

    frame = load_processed_dataset(processed_path)
    splits = assign_splits(frame)
    output = pd.DataFrame(
        {
            "match_id": frame["match_id"],
            "season": frame["season"],
            "split": splits,
        }
    )
    splits_path = Path(splits_output_path)
    splits_path.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(splits_path, index=False)

    manifest = build_split_manifest(processed_path, frame)
    manifest_path = Path(manifest_output_path)
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def verify_preprocessing_split_contract(
    processed_path: str | Path,
    splits_path: str | Path,
    manifest_path: str | Path,
) -> dict[str, Any]:
    """Comprueba que los splits congelados corresponden al dataset procesado.

    Esta comprobación se ejecuta antes del gate ``Data Ready`` para impedir que
    una regeneración del preprocesamiento deje índices, conteos o huellas de
    partición desalineados.
    """

    processed = Path(processed_path)
    split_file = Path(splits_path)
    manifest_file = Path(manifest_path)
    frame = load_processed_dataset(processed)
    splits = pd.read_csv(split_file, dtype={"match_id": "string", "season": "string", "split": "string"})
    expected_columns = {"match_id", "season", "split"}
    if set(splits.columns) != expected_columns:
        raise ValueError(f"Contrato de splits inválido; se esperaban {expected_columns}.")
    if splits["match_id"].duplicated().any():
        raise ValueError("El archivo de splits contiene match_id duplicados.")

    expected = pd.DataFrame(
        {
            "match_id": frame["match_id"].astype("string"),
            "season": frame["season"].astype("string"),
            "split": assign_splits(frame),
        }
    )
    observed = splits.loc[:, ["match_id", "season", "split"]].copy()
    if len(observed) != len(expected) or set(observed["match_id"]) != set(expected["match_id"]):
        raise ValueError("Los splits no cubren exactamente los match_id del dataset procesado.")

    comparison = expected.merge(observed, on="match_id", how="inner", suffixes=("_expected", "_observed"))
    if not comparison["season_expected"].eq(comparison["season_observed"]).all():
        raise ValueError("La temporada de uno o más match_id no coincide entre datos y splits.")
    if not comparison["split_expected"].eq(comparison["split_observed"]).all():
        raise ValueError("La asignación congelada de uno o más match_id no coincide.")

    manifest = json.loads(manifest_file.read_text(encoding="utf-8"))
    expected_counts = split_row_counts(frame)
    if manifest["source_dataset"]["sha256"] != file_sha256(processed):
        raise ValueError("La huella del manifest no coincide con el dataset procesado.")
    if manifest["source_dataset"]["rows"] != len(frame) or manifest["row_counts"] != expected_counts:
        raise ValueError("Las dimensiones o conteos del manifest no coinciden con los splits.")

    return {
        "status": "verified",
        "processed_dataset_sha256": file_sha256(processed),
        "processed_rows": int(len(frame)),
        "split_rows": int(len(observed)),
        "row_counts": expected_counts,
        "test_seasons": TEST_SEASONS,
    }


if __name__ == "__main__":
    manifest = freeze_splits(
        processed_path="data/processed/laliga_matches_clean.csv",
        splits_output_path="data/processed/splits/laliga_splits.csv",
        manifest_output_path="reports/metrics/split_manifest.json",
    )
    verification = verify_preprocessing_split_contract(
        processed_path="data/processed/laliga_matches_clean.csv",
        splits_path="data/processed/splits/laliga_splits.csv",
        manifest_path="reports/metrics/split_manifest.json",
    )
    print(json.dumps({"manifest": manifest["row_counts"], "verification": verification}, ensure_ascii=False))
