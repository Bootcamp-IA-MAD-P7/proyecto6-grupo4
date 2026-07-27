from __future__ import annotations

import numpy as np
import pandas as pd

from src.candidates.ensemble import build_ensemble_pipeline
from src.data.historical_features import MODEL_FEATURES


def _sample() -> tuple[pd.DataFrame, pd.Series]:
    rows = 9
    frame = pd.DataFrame({"home_team": ["A", "B", "C"] * 3, "away_team": ["B", "C", "A"] * 3, **{column: [float(index + row) for row in range(rows)] for index, column in enumerate(MODEL_FEATURES[2:])}})
    return frame, pd.Series(["H", "D", "A"] * 3)


def test_ensemble_fits_only_the_common_feature_schema_and_predicts_valid_classes() -> None:
    features, labels = _sample()
    pipeline = build_ensemble_pipeline()
    pipeline.fit(features.loc[:, MODEL_FEATURES], labels)
    assert set(pipeline.predict(features.loc[:, MODEL_FEATURES])).issubset({"H", "D", "A"})


def test_ensemble_is_a_soft_voting_combination_of_the_approved_logistic_and_svc() -> None:
    voting = build_ensemble_pipeline().named_steps["classifier"]
    assert voting.voting == "soft"
    estimator_names = {name for name, _ in voting.estimators}
    assert estimator_names == {"logistic_a", "svc_d"}
    estimators = dict(voting.estimators)
    assert estimators["svc_d"].kernel == "rbf"
    assert estimators["svc_d"].probability is True


def test_ensemble_exposes_predict_proba_over_the_three_classes() -> None:
    features, labels = _sample()
    pipeline = build_ensemble_pipeline()
    pipeline.fit(features.loc[:, MODEL_FEATURES], labels)
    probabilities = pipeline.predict_proba(features.loc[:, MODEL_FEATURES])
    assert probabilities.shape == (len(features), 3)
    assert np.allclose(probabilities.sum(axis=1), 1.0)
