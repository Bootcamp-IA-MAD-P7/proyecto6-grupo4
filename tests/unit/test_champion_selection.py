from __future__ import annotations

import json

import pandas as pd
import pytest

from src.evaluation.champion import (
    select_and_evaluate_champion,
    select_and_promote_champion,
)


def _metrics(candidate_id, macro_f1, gap, artifact_path, **overrides):
    base = {
        "candidate_id": candidate_id,
        "model_version": f"{candidate_id.lower()}_v1",
        "data_version_sha256": "sha_data",
        "features_sha256": "sha_features",
        "feature_generator_version": "historical_features_v1",
        "split_manifest_reference": "reports/metrics/split_manifest.json",
        "overfitting_gap_macro_f1": gap,
        "validation": {"macro_f1": macro_f1, "accuracy": 0.5, "balanced_accuracy": 0.5, "log_loss": 1.0},
        "train": {"macro_f1": macro_f1 + gap, "accuracy": 0.5, "balanced_accuracy": 0.5, "log_loss": 1.0},
        "inference_time_ms_per_row": 1.0,
        "artifact_path": artifact_path,
    }
    base.update(overrides)
    return base


def _write_json(path, content) -> str:
    path.write_text(json.dumps(content), encoding="utf-8")
    return str(path)


def _dummy_pipeline():
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.compose import ColumnTransformer
    from sklearn.impute import SimpleImputer
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES

    pre = ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), list(MODEL_NUMERIC_FEATURES)),
        ("teams", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), list(MODEL_CATEGORICAL_FEATURES)),
    ])
    return Pipeline([("preprocessing", pre), ("classifier", LogisticRegression(max_iter=200, random_state=42))])


def _write_features_and_fit_artifact(tmp_path):
    import joblib
    from src.data.historical_features import MODEL_FEATURES
    from src.data.laliga_loader import TARGET_COLUMN

    rows = 60
    dates = pd.date_range("2020-01-01", periods=rows, freq="7D")
    frame = pd.DataFrame({
        "match_id": [f"m{i}" for i in range(rows)],
        "match_date": dates,
        "split": ["train"] * 30 + ["validation"] * 15 + ["test"] * 15,
        "home_team": (["A", "B", "C"] * (rows // 3)),
        "away_team": (["B", "C", "A"] * (rows // 3)),
        TARGET_COLUMN: (["H", "D", "A"] * (rows // 3)),
        **{column: [float((index + row) % 5) for row in range(rows)] for index, column in enumerate(MODEL_FEATURES[2:])},
    })
    features_path = tmp_path / "features.csv"
    frame.to_csv(features_path, index=False)

    pipeline = _dummy_pipeline()
    train = frame.loc[frame["split"].eq("train")]
    pipeline.fit(train.loc[:, MODEL_FEATURES], train[TARGET_COLUMN])
    artifact_path = tmp_path / "candidate.joblib"
    joblib.dump(pipeline, artifact_path)

    source_path = tmp_path / "source.csv"
    pd.DataFrame({"a": [1]}).to_csv(source_path, index=False)
    return features_path, source_path, str(artifact_path)


def test_champion_is_chosen_by_highest_validation_macro_f1_among_eligible(tmp_path) -> None:
    features_path, source_path, artifact_path = _write_features_and_fit_artifact(tmp_path)
    path_a = _write_json(tmp_path / "a.json", _metrics("A", 0.40, 0.01, artifact_path))
    path_b = _write_json(tmp_path / "b.json", _metrics("B", 0.55, 0.02, artifact_path))  # el mejor
    path_c = _write_json(tmp_path / "c.json", _metrics("C", 0.90, 0.20, artifact_path))  # descalificado por gap

    result = select_and_evaluate_champion(
        metrics_paths=[path_a, path_b, path_c],
        features_path=features_path,
        source_dataset_path=source_path,
        artifact_path=tmp_path / "champion.joblib",
        metadata_path=tmp_path / "champion_metadata.json",
        final_metrics_path=tmp_path / "champion_test_metrics.json",
    )
    assert result["champion_candidate_id"] == "B"
    assert result["test_used_once"] is True
    assert (tmp_path / "champion.joblib").exists()
    assert len(result["artifact_sha256"]) == 64
    assert result["artifact_descriptor"]["root_type"] == "Pipeline"
    assert result["artifact_descriptor"]["classifier_type"] == "LogisticRegression"


def test_champion_selection_raises_when_no_candidate_meets_overfitting_threshold(tmp_path) -> None:
    features_path, source_path, artifact_path = _write_features_and_fit_artifact(tmp_path)
    path_a = _write_json(tmp_path / "a.json", _metrics("A", 0.40, 0.30, artifact_path))
    path_b = _write_json(tmp_path / "b.json", _metrics("B", 0.55, 0.40, artifact_path))

    with pytest.raises(ValueError, match="umbral de overfitting"):
        select_and_evaluate_champion(
            metrics_paths=[path_a, path_b],
            features_path=features_path,
            source_dataset_path=source_path,
            artifact_path=tmp_path / "champion.joblib",
            metadata_path=tmp_path / "champion_metadata.json",
            final_metrics_path=tmp_path / "champion_test_metrics.json",
        )


def test_champion_selection_raises_when_candidates_are_not_comparable(tmp_path) -> None:
    features_path, source_path, artifact_path = _write_features_and_fit_artifact(tmp_path)
    path_a = _write_json(tmp_path / "a.json", _metrics("A", 0.40, 0.01, artifact_path))
    path_b = _write_json(tmp_path / "b.json", _metrics("B", 0.55, 0.02, artifact_path, data_version_sha256="different_sha"))

    with pytest.raises(ValueError, match="no son comparables"):
        select_and_evaluate_champion(
            metrics_paths=[path_a, path_b],
            features_path=features_path,
            source_dataset_path=source_path,
            artifact_path=tmp_path / "champion.joblib",
            metadata_path=tmp_path / "champion_metadata.json",
            final_metrics_path=tmp_path / "champion_test_metrics.json",
        )


def test_champion_selection_never_uses_test_rows_to_pick_the_winner(tmp_path) -> None:
    # B gana en validation aunque A hipoteticamente pudiera rendir mejor en test:
    # la eleccion no debe usar test en absoluto (se verifica indirectamente
    # comprobando que el ganador es 100% determinado por 'validation').
    features_path, source_path, artifact_path = _write_features_and_fit_artifact(tmp_path)
    path_a = _write_json(tmp_path / "a.json", _metrics("A", 0.50, 0.01, artifact_path))
    path_b = _write_json(tmp_path / "b.json", _metrics("B", 0.51, 0.01, artifact_path))

    result = select_and_evaluate_champion(
        metrics_paths=[path_a, path_b],
        features_path=features_path,
        source_dataset_path=source_path,
        artifact_path=tmp_path / "champion.joblib",
        metadata_path=tmp_path / "champion_metadata.json",
        final_metrics_path=tmp_path / "champion_test_metrics.json",
    )
    assert result["champion_candidate_id"] == "B"
    assert result["test_rows"] == 15


def test_champion_promotion_fits_train_and_validation_without_evaluating_test(
    tmp_path,
    monkeypatch,
) -> None:
    features_path, source_path, artifact_path = _write_features_and_fit_artifact(tmp_path)
    features = pd.read_csv(features_path)
    features.loc[features["split"].eq("test"), "result_label"] = "BROKEN_TEST_LABEL"
    features.to_csv(features_path, index=False)

    path_a = _write_json(
        tmp_path / "a.json",
        _metrics("A", 0.50, 0.01, artifact_path),
    )
    path_b = _write_json(
        tmp_path / "b.json",
        _metrics("B", 0.51, 0.01, artifact_path),
    )
    historical_test_path = tmp_path / "historical_test.json"
    historical_test_path.write_text('{"status":"frozen"}', encoding="utf-8")

    def fail_if_test_is_evaluated(*_args, **_kwargs):
        raise AssertionError("La promoción no debe calcular métricas.")

    monkeypatch.setattr(
        "src.evaluation.champion.metric_summary",
        fail_if_test_is_evaluated,
    )

    result = select_and_promote_champion(
        metrics_paths=[path_a, path_b],
        features_path=features_path,
        source_dataset_path=source_path,
        artifact_path=tmp_path / "promoted.joblib",
        metadata_path=tmp_path / "champion_metadata.json",
        historical_test_metrics_path=historical_test_path,
    )

    assert result["champion_candidate_id"] == "B"
    assert result["promotion_contract"] == {
        "fit_splits": ["train", "validation"],
        "fit_rows": 45,
        "test_rows_used": 0,
        "test_metrics_recomputed": False,
    }
    assert result["historical_test_evidence"]["status"] == "frozen_not_recomputed"
    assert "test" not in result
    assert "test_confusion_matrix" not in result
    assert (tmp_path / "promoted.joblib").exists()
