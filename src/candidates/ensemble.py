"""T-4.1: ensemble comparable de los candidatos que superan el gap de overfitting.

Combina, por votación suave (promedio de probabilidades), los únicos dos
candidatos que quedaron `ready_for_comparison` en T-2.5: A (logística
multinomial) y D (SVC RBF, el Champion actual). B y C quedaron
descalificados por sobreajuste (`overfitting_gap_macro_f1` > 0.05) y no
entran al ensemble para no arrastrar ese sobreajuste.

Reutiliza los mismos hiperparámetros ya aprobados de A y D: este módulo no
reajusta ni afina nada (eso es T-4.2); solo mide si combinarlos aporta sobre
el mejor individual.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import VotingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

from src.candidates.common import train_candidate
from src.candidates.model_a.pipeline import build_pipeline_a
from src.candidates.model_b.pipeline import build_pipeline_b
from src.candidates.model_c.pipeline import build_pipeline_c
from src.candidates.model_d.pipeline import build_pipeline_d
from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES

ENSEMBLE_SEED = 42
ENSEMBLE_VERSION = "ensemble_ad_soft_voting_v1"
ENSEMBLE_ABCD_VERSION = "ensemble_abcd_soft_voting_v1"


def build_ensemble_pipeline(seed: int = ENSEMBLE_SEED) -> Pipeline:
    """Preprocesamiento común + votación suave entre la logística A y el SVC D."""

    preprocessing = ColumnTransformer(
        transformers=[
            (
                "numeric",
                Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]),
                list(MODEL_NUMERIC_FEATURES),
            ),
            (
                "teams",
                Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]),
                list(MODEL_CATEGORICAL_FEATURES),
            ),
        ],
        remainder="drop",
    )
    voting = VotingClassifier(
        estimators=[
            (
                "logistic_a",
                LogisticRegression(solver="lbfgs", l1_ratio=0.0, C=0.1, max_iter=2000, class_weight="balanced", random_state=seed),
            ),
            (
                "svc_d",
                SVC(kernel="rbf", C=0.5, gamma="scale", probability=True, class_weight="balanced", random_state=seed),
            ),
        ],
        voting="soft",
    )
    return Pipeline([("preprocessing", preprocessing), ("classifier", voting)])


def train_ensemble(**paths: Any) -> dict[str, Any]:
    """Ajusta el ensemble solo en train y mide en validation, igual que A-D."""

    return train_candidate(
        candidate_id="ENSEMBLE_AD",
        member="I1_I2",
        algorithm="VotingClassifier soft (logística A + SVC RBF D)",
        model_version=ENSEMBLE_VERSION,
        pipeline=build_ensemble_pipeline(),
        seed=ENSEMBLE_SEED,
        transformations_summary=(
            "Mismo preprocesamiento de A/D (imputación mediana + StandardScaler numéricos; "
            "moda + one-hot equipos); votación suave promedia predict_proba de ambos "
            "estimadores base, cada uno ajustado internamente solo en train."
        ),
        limitations=(
            "No incluye B ni C (descalificados por sobreajuste en T-2.5); duplica el costo de "
            "inferencia de A+D; hereda el cold-start de equipos nuevos y no usa cuotas; test reservado."
        ),
        **paths,
    )


def build_ensemble_pipeline_abcd(seed: int = ENSEMBLE_SEED) -> Pipeline:
    """Votación suave entre los cuatro candidatos, cada uno con su propio preprocesamiento.

    A diferencia de `build_ensemble_pipeline`, aquí cada estimador ya es un
    Pipeline completo (preprocesamiento + clasificador) porque B usa
    codificación ordinal de equipos mientras A, C y D usan one-hot: no
    comparten un único `ColumnTransformer` de nivel superior.
    """

    voting = VotingClassifier(
        estimators=[
            ("logistic_a", build_pipeline_a(seed)),
            ("hgb_b", build_pipeline_b(seed)),
            ("rf_c", build_pipeline_c(seed)),
            ("svc_d", build_pipeline_d(seed)),
        ],
        voting="soft",
    )
    return Pipeline([("classifier", voting)])


def train_ensemble_abcd(**paths: Any) -> dict[str, Any]:
    """Ajusta el ensemble de 4 candidatos solo en train y mide en validation."""

    return train_candidate(
        candidate_id="ENSEMBLE_ABCD",
        member="I1_I2_I3_I4",
        algorithm="VotingClassifier soft (A logística + B HistGB retunado + C RandomForest regularizado + D SVC RBF)",
        model_version=ENSEMBLE_ABCD_VERSION,
        pipeline=build_ensemble_pipeline_abcd(),
        seed=ENSEMBLE_SEED,
        transformations_summary=(
            "Cada candidato conserva su propio preprocesamiento aprobado (A/C/D one-hot + "
            "escalado donde aplica; B ordinal); votación suave promedia los cuatro "
            "predict_proba, cada uno ajustado internamente solo en train."
        ),
        limitations=(
            "B usa la configuración retunada de T-4.2 adelantado (gap 0.376 -> 0.042); C usa la "
            "configuración regularizada de I3 (gap 0.256 -> 0.000); cuadruplica el costo de "
            "inferencia frente a un candidato individual; cold-start de equipos nuevos; no usa "
            "cuotas; test reservado."
        ),
        **paths,
    )
