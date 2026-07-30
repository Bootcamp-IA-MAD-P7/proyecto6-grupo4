"""Pipeline C comparable: random forest."""
from __future__ import annotations
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from src.candidates.common import train_candidate
from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES

MODEL_C_SEED = 42
def build_pipeline_c(seed: int = MODEL_C_SEED) -> Pipeline:
    pre = ColumnTransformer([("numeric", SimpleImputer(strategy="median"), list(MODEL_NUMERIC_FEATURES)), ("teams", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), list(MODEL_CATEGORICAL_FEATURES))])
    return Pipeline([("preprocessing", pre), ("classifier", RandomForestClassifier(n_estimators=300, max_depth=6, min_samples_leaf=15, min_samples_split=30, max_features="sqrt", class_weight="balanced", n_jobs=-1, random_state=seed))])
def train_candidate_c(**paths):
    return train_candidate(candidate_id="C", member="I3", algorithm="RandomForestClassifier", model_version="candidate_c_random_forest_v1", pipeline=build_pipeline_c(), seed=MODEL_C_SEED, transformations_summary="Imputación mediana numérica; moda + one-hot de equipos; ajustado solo en train. Regularizado (max_depth=6, min_samples_leaf=15, min_samples_split=30) para cerrar el gap de overfitting (0.256 -> 0.000) frente al ajuste inicial.", limitations="No usa cuotas; cold-start para equipos nuevos; test reservado.", **paths)
