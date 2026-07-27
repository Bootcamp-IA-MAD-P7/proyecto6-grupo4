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


def test_candidate_b_c_and_d_fit_only_the_common_feature_schema() -> None:
    features, labels = _sample()
    for pipeline in (build_pipeline_b(), build_pipeline_c(), build_pipeline_d()):
        pipeline.fit(features.loc[:, MODEL_FEATURES], labels)
        assert set(pipeline.predict(features.loc[:, MODEL_FEATURES])).issubset({"H", "D", "A"})


def test_pipeline_d_is_the_approved_probabilistic_rbf_svm() -> None:
    classifier = build_pipeline_d().named_steps["classifier"]
    assert classifier.kernel == "rbf"
    assert classifier.probability is True
