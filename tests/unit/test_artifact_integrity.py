from __future__ import annotations

import json

import joblib
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC

from src.evaluation.artifact_integrity import (
    build_artifact_identity,
    verify_champion_artifact,
)


def _ensemble() -> Pipeline:
    voting = VotingClassifier(
        estimators=[
            ("logistic_a", LogisticRegression()),
            ("hgb_b", LogisticRegression()),
            ("rf_c", LogisticRegression()),
            ("svc_d", LogisticRegression()),
        ],
        voting="soft",
    )
    return Pipeline([("classifier", voting)])


def _metadata_for(artifact_path) -> dict:
    return {
        "champion_candidate_id": "ENSEMBLE_ABCD",
        "champion_model_version": "ensemble_abcd_soft_voting_v1",
        **build_artifact_identity(artifact_path),
    }


def test_valid_ensemble_matches_its_hash_and_descriptor(tmp_path) -> None:
    artifact = tmp_path / "champion.joblib"
    metadata = tmp_path / "metadata.json"
    joblib.dump(_ensemble(), artifact)
    metadata.write_text(
        json.dumps(_metadata_for(artifact)),
        encoding="utf-8",
    )

    result = verify_champion_artifact(artifact, metadata)

    assert result["valid"] is True
    assert result["errors"] == []
    assert result["artifact_descriptor"]["estimator_names"] == [
        "logistic_a",
        "hgb_b",
        "rf_c",
        "svc_d",
    ]


def test_svc_cannot_be_published_as_the_abcd_ensemble(tmp_path) -> None:
    intended_artifact = tmp_path / "intended.joblib"
    actual_artifact = tmp_path / "actual.joblib"
    metadata = tmp_path / "metadata.json"
    joblib.dump(_ensemble(), intended_artifact)
    joblib.dump(Pipeline([("classifier", SVC(probability=True))]), actual_artifact)
    metadata.write_text(
        json.dumps(_metadata_for(intended_artifact)),
        encoding="utf-8",
    )

    result = verify_champion_artifact(actual_artifact, metadata)

    assert result["valid"] is False
    assert "El SHA-256 del artefacto no coincide con la metadata." in result["errors"]
    assert (
        "ENSEMBLE_ABCD debe contener VotingClassifier como clasificador."
        in result["errors"]
    )


def test_missing_artifact_identity_is_rejected(tmp_path) -> None:
    artifact = tmp_path / "champion.joblib"
    metadata = tmp_path / "metadata.json"
    joblib.dump(_ensemble(), artifact)
    metadata.write_text(
        json.dumps(
            {
                "champion_candidate_id": "ENSEMBLE_ABCD",
                "champion_model_version": "ensemble_abcd_soft_voting_v1",
            }
        ),
        encoding="utf-8",
    )

    result = verify_champion_artifact(artifact, metadata)

    assert result["valid"] is False
    assert "La metadata no declara artifact_sha256." in result["errors"]
    assert "La metadata no declara artifact_descriptor." in result["errors"]
