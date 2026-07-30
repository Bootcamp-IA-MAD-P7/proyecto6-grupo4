"""Pipeline B comparable: HistGradientBoosting con codificación segura."""
from __future__ import annotations
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder
from src.candidates.common import train_candidate
from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES

MODEL_B_SEED = 42
def build_pipeline_b(seed: int = MODEL_B_SEED) -> Pipeline:
    pre = ColumnTransformer([("numeric", SimpleImputer(strategy="median"), list(MODEL_NUMERIC_FEATURES)), ("teams", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ordinal", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1))]), list(MODEL_CATEGORICAL_FEATURES))])
    return Pipeline([("preprocessing", pre), ("classifier", HistGradientBoostingClassifier(
        learning_rate=.025, max_iter=300, max_leaf_nodes=19, min_samples_leaf=20,
        l2_regularization=1.0, class_weight="balanced",
        early_stopping=True, validation_fraction=.15, n_iter_no_change=15,
        random_state=seed,
    ))])
def train_candidate_b(**paths):
    return train_candidate(candidate_id="B", member="I2", algorithm="HistGradientBoostingClassifier", model_version="candidate_b_hist_gradient_boosting_v1", pipeline=build_pipeline_b(), seed=MODEL_B_SEED, transformations_summary="Imputación mediana numérica; moda + ordinal de equipos; ajustado solo en train. Retunado (T-4.2): early_stopping interno + max_leaf_nodes=19 + min_samples_leaf=20 + l2_regularization=1.0 + class_weight=balanced, elegido por grid search reproducible de 256 combinaciones sobre validation (scripts/tune_candidate_b.py, reports/experiments/candidate_b_tuning_search.json). Tras corregir el dataset (alias Villarreal), l2_regularization se subió de 0.5 a 1.0 para volver a cumplir el gap < 0.05.", limitations="No usa cuotas; cold-start para equipos nuevos; test reservado.", **paths)
