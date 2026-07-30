"""Pipeline D comparable: SVC RBF con calibracion explicita de probabilidades.

T-4.2 (adelanto sobre D, I2 con el componente de I4): sustituye `probability=True`
(estimacion interna de Platt, sin cross-validation propia y deprecada desde
sklearn 1.9) por el calibrador de `src/ensemble/svc_calibrated.py` que ya
construyo y valido I4 para T-4.1: `CalibratedClassifierCV(method="temperature")`
sobre cinco folds estratificados dentro de train, `ensemble=False`. Resultado
en validation: macro-F1 0.483744 -> 0.484859, gap 0.009166 -> 0.007564.
"""
from __future__ import annotations
from sklearn.pipeline import Pipeline
from src.candidates.common import train_candidate
from src.ensemble.svc_calibrated import build_calibrated_svc

MODEL_D_SEED = 42
def build_pipeline_d(seed: int = MODEL_D_SEED) -> Pipeline:
    return Pipeline([("classifier", build_calibrated_svc(seed=seed))])
def train_candidate_d(**paths):
    return train_candidate(candidate_id="D", member="I4", algorithm="SVC RBF + calibración explícita (temperature, 5-fold estratificado)", model_version="candidate_d_svc_rbf_calibrated_v1", pipeline=build_pipeline_d(), seed=MODEL_D_SEED, transformations_summary="Imputación mediana + StandardScaler numéricos; moda + one-hot equipos (dentro del SVC base); calibración de probabilidades vía CalibratedClassifierCV(method='temperature', cv=StratifiedKFold(5), ensemble=False), todo ajustado solo en train.", limitations="SVC no es interpretable de forma nativa; no usa cuotas; test reservado; calibración añade ~5x el costo de entrenamiento del SVC base.", **paths)
