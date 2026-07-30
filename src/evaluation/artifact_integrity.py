"""Verificación reproducible entre el artefacto Champion y su metadata.

El SHA-256 demuestra que se cargó exactamente el binario publicado. El
descriptor semántico comprueba además que ese binario contiene la familia de
modelo declarada; por ejemplo, un Champion ``ENSEMBLE_ABCD`` debe ser una
votación suave con los cuatro miembros acordados.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import joblib
from sklearn.ensemble import VotingClassifier
from sklearn.pipeline import Pipeline

from src.data.laliga_loader import file_sha256


ENSEMBLE_ABCD_MEMBERS = ("logistic_a", "hgb_b", "rf_c", "svc_d")


def _terminal_estimator_type(estimator: Any) -> str:
    """Devuelve el estimador final, atravesando pipelines anidados."""

    current = estimator
    while isinstance(current, Pipeline) and current.steps:
        current = current.steps[-1][1]
    return type(current).__name__


def describe_model(estimator: Any) -> dict[str, Any]:
    """Construye una firma pequeña y estable de la estructura del modelo."""

    classifier = estimator
    pipeline_steps: list[str] = []
    if isinstance(estimator, Pipeline):
        pipeline_steps = [name for name, _ in estimator.steps]
        classifier = estimator.steps[-1][1]

    descriptor: dict[str, Any] = {
        "root_type": type(estimator).__name__,
        "pipeline_steps": pipeline_steps,
        "classifier_type": type(classifier).__name__,
        "classes": [str(label) for label in getattr(estimator, "classes_", [])],
    }
    if isinstance(classifier, VotingClassifier):
        members = list(classifier.estimators)
        descriptor.update(
            {
                "voting": classifier.voting,
                "estimator_names": [name for name, _ in members],
                "member_classifier_types": {
                    name: _terminal_estimator_type(member)
                    for name, member in members
                },
            }
        )
    return descriptor


def build_artifact_identity(artifact_path: str | Path) -> dict[str, Any]:
    """Calcula la identidad que debe incorporarse a la metadata del Champion."""

    artifact = Path(artifact_path)
    estimator = joblib.load(artifact)
    return {
        "artifact_sha256": file_sha256(artifact),
        "artifact_descriptor": describe_model(estimator),
    }


def verify_champion_artifact(
    artifact_path: str | Path,
    metadata_path: str | Path,
) -> dict[str, Any]:
    """Compara el binario con su metadata sin reentrenar ni evaluar el modelo."""

    artifact = Path(artifact_path)
    metadata_file = Path(metadata_path)
    metadata = json.loads(metadata_file.read_text(encoding="utf-8"))
    identity = build_artifact_identity(artifact)
    descriptor = identity["artifact_descriptor"]
    errors: list[str] = []

    expected_sha = metadata.get("artifact_sha256")
    if expected_sha is None:
        errors.append("La metadata no declara artifact_sha256.")
    elif expected_sha != identity["artifact_sha256"]:
        errors.append("El SHA-256 del artefacto no coincide con la metadata.")

    expected_descriptor = metadata.get("artifact_descriptor")
    if expected_descriptor is None:
        errors.append("La metadata no declara artifact_descriptor.")
    elif expected_descriptor != descriptor:
        errors.append("La estructura del artefacto no coincide con la metadata.")

    if metadata.get("champion_candidate_id") == "ENSEMBLE_ABCD":
        if descriptor["classifier_type"] != "VotingClassifier":
            errors.append(
                "ENSEMBLE_ABCD debe contener VotingClassifier como clasificador."
            )
        if descriptor.get("voting") != "soft":
            errors.append("ENSEMBLE_ABCD debe utilizar votación suave.")
        if descriptor.get("estimator_names") != list(ENSEMBLE_ABCD_MEMBERS):
            errors.append(
                "ENSEMBLE_ABCD no contiene exactamente los cuatro miembros acordados."
            )

    return {
        "valid": not errors,
        "artifact_path": artifact.as_posix(),
        "metadata_path": metadata_file.as_posix(),
        "champion_candidate_id": metadata.get("champion_candidate_id"),
        "champion_model_version": metadata.get("champion_model_version"),
        **identity,
        "errors": errors,
    }
