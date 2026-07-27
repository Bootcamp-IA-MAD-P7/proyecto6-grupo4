"""Pipeline D comparable: SVC RBF con probabilidades."""
from __future__ import annotations
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC
from src.candidates.common import train_candidate
from src.data.historical_features import MODEL_CATEGORICAL_FEATURES, MODEL_NUMERIC_FEATURES

MODEL_D_SEED = 42
def build_pipeline_d(seed: int = MODEL_D_SEED) -> Pipeline:
    pre = ColumnTransformer([("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")), ("scaler", StandardScaler())]), list(MODEL_NUMERIC_FEATURES)), ("teams", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("one_hot", OneHotEncoder(handle_unknown="ignore"))]), list(MODEL_CATEGORICAL_FEATURES))])
    return Pipeline([("preprocessing", pre), ("classifier", SVC(kernel="rbf", C=.5, gamma="scale", probability=True, class_weight="balanced", random_state=seed))])
def train_candidate_d(**paths):
    return train_candidate(candidate_id="D", member="I4", algorithm="SVC RBF probabilistic", model_version="candidate_d_svc_rbf_v1", pipeline=build_pipeline_d(), seed=MODEL_D_SEED, transformations_summary="Imputación mediana + StandardScaler numéricos; moda + one-hot equipos; ajustado solo en train.", limitations="SVC no es interpretable de forma nativa; no usa cuotas; test reservado.", **paths)
