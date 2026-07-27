from __future__ import annotations

import pandas as pd

from src.candidates.model_b.pipeline import build_pipeline_b
from src.candidates.model_c.pipeline import build_pipeline_c
from src.candidates.model_d.pipeline import build_pipeline_d
from src.data.historical_features import MODEL_FEATURES


def _sample() -> tuple[pd.DataFrame, pd.Series]:
    rows = 9
    frame = pd.DataFrame({"home_team": ["A", "B", "C"] * 3, "away_team": ["B", "C", "A"] * 3, **{column: [float(index + row) for row in range(rows)] for index, column in enumerate(MODEL_FEATURES[2:])}})
    return frame, pd.Series(["H", "D", "A"] * 3)


def _larger_sample() -> tuple[pd.DataFrame, pd.Series]:
    # build_pipeline_b usa early_stopping interno (validation_fraction=.15); necesita
    # suficientes filas por clase para poder separar su propio holdout interno.
    rows = 60
    frame = pd.DataFrame({"home_team": ["A", "B", "C"] * 20, "away_team": ["B", "C", "A"] * 20, **{column: [float((index + row) % 7) for row in range(rows)] for index, column in enumerate(MODEL_FEATURES[2:])}})
    return frame, pd.Series(["H", "D", "A"] * 20)


def test_candidate_b_c_and_d_fit_only_the_common_feature_schema() -> None:
    features, labels = _larger_sample()
    for pipeline in (build_pipeline_b(), build_pipeline_c(), build_pipeline_d()):
        pipeline.fit(features.loc[:, MODEL_FEATURES], labels)
        assert set(pipeline.predict(features.loc[:, MODEL_FEATURES])).issubset({"H", "D", "A"})


def test_pipeline_d_is_the_calibrated_rbf_svm() -> None:
    # T-4.2: D ya no usa el probability=True interno (deprecado desde sklearn
    # 1.9); calibra explícitamente con CalibratedClassifierCV (I4, T-4.1).
    calibrator = build_pipeline_d().named_steps["classifier"]
    assert calibrator.method == "temperature"
    assert calibrator.ensemble is False
    assert calibrator.cv.get_n_splits() == 5
    base_svc = calibrator.estimator.named_steps["classifier"]
    assert base_svc.kernel == "rbf"
    # No pasa probability=True: la calibración explícita reemplaza la
    # estimación interna deprecada, así que el parámetro queda en su default.
    assert base_svc.probability != True  # noqa: E712 (comparación explícita contra el sentinel "deprecated")
