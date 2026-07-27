from __future__ import annotations

import pandas as pd

from src.candidates.model_a.pipeline import MODEL_A_SEED, build_pipeline_a
from src.data.historical_features import MODEL_FEATURES


def test_pipeline_a_fits_transformations_only_on_training_rows() -> None:
    train = pd.DataFrame(
        {
            "home_team": ["Alpha", "Beta", "Gamma", "Alpha", "Beta", "Gamma"],
            "away_team": ["Beta", "Gamma", "Alpha", "Gamma", "Alpha", "Beta"],
            **{column: [float(index + row) for row in range(6)] for index, column in enumerate(MODEL_FEATURES[2:])},
        }
    )
    labels = pd.Series(["H", "D", "A", "H", "D", "A"])
    pipeline = build_pipeline_a(MODEL_A_SEED)

    pipeline.fit(train.loc[:, MODEL_FEATURES], labels)
    predictions = pipeline.predict(train.loc[:, MODEL_FEATURES])

    assert set(predictions).issubset({"H", "D", "A"})
    assert pipeline.named_steps["classifier"].solver == "lbfgs"
    assert pipeline.named_steps["classifier"].classes_.tolist() == ["A", "D", "H"]
