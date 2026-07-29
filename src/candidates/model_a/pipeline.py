"""Entrenamiento reproducible del candidato A sin consultar el test protegido."""

from __future__ import annotations

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.candidates.common import train_candidate
from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES


MODEL_A_SEED = 42
MODEL_A_VERSION = "candidate_a_logistic_regression_v1"


def build_pipeline_a(seed: int = MODEL_A_SEED) -> Pipeline:
    """Construye el pipeline completo; imputación y escala se ajustan en train."""

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="median")),
                    ("scaler", StandardScaler()),
                ]),
                list(MODEL_NUMERIC_FEATURES),
            ),
            (
                "teams",
                Pipeline([
                    ("imputer", SimpleImputer(strategy="most_frequent")),
                    ("one_hot", OneHotEncoder(handle_unknown="ignore")),
                ]),
                list(MODEL_CATEGORICAL_FEATURES),
            ),
        ],
        remainder="drop",
    )
    return Pipeline([
        ("preprocessing", preprocessing),
        (
            "classifier",
            LogisticRegression(
                solver="lbfgs",
                l1_ratio=0.0,
                C=0.1,
                max_iter=2000,
                class_weight="balanced",
                random_state=seed,
            ),
        ),
    ])


def train_candidate_a(**paths):
    return train_candidate(
        candidate_id="A",
        member="I1",
        algorithm="Regresión logística multinomial",
        model_version=MODEL_A_VERSION,
        pipeline=build_pipeline_a(MODEL_A_SEED),
        seed=MODEL_A_SEED,
        transformations_summary=(
            "Imputación mediana + StandardScaler numéricos; moda + OneHot equipos; "
            "ajustado solo en train."
        ),
        limitations=(
            "No usa cuotas; la primera aparición de equipos usa valores cold-start; "
            "test reservado."
        ),
        **paths,
    )
