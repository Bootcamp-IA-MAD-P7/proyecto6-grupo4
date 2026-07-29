"""Ensembles de candidatos: A+D (histórico, T-4.1) y A+B+C+D (vigente, T-2.6).

`build_ensemble_pipeline_abcd` / `train_ensemble_abcd` son el flujo VIGENTE:
producen el Champion actual (`ENSEMBLE_ABCD`, ver
`reports/experiments/champion_metadata.json`), con los cuatro candidatos.

`build_ensemble_pipeline` / `train_ensemble` (sufijo `_AD`, `candidate_id`
`ENSEMBLE_AD`) son el ensemble ORIGINAL de T-4.1, cuando solo A y D habían
superado el gap de overfitting en T-2.5 (B y C fueron descalificados en esa
ronda y luego re-tuneados/regularizados hasta calificar en T-4.2/T-2.6). Se
conserva por trazabilidad histórica y porque sus tests (`ENSEMBLE_AD` en
`tests/unit/test_ensemble_pipeline.py`) documentan ese punto del proyecto,
pero NINGÚN script de producción ni de selección de Champion lo usa: no lo
ejecutes esperando obtener el Champion vigente, usa `run_ensemble_abcd.py`.
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
    """[HISTÓRICO T-4.1] Preprocesamiento común + votación suave entre A y D.

    Superado por `build_ensemble_pipeline_abcd`. Usa `SVC(probability=True)`,
    deprecado desde sklearn 1.9; se mantiene sin cambios para no alterar la
    evidencia histórica ya registrada de T-4.1.
    """

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
    """[HISTÓRICO T-4.1] Ajusta el ensemble A+D solo en train y mide en validation.

    No es el flujo de promoción del Champion; usa `train_ensemble_abcd` para eso.
    """

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
