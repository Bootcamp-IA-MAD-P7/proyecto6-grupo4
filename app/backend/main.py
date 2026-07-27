from __future__ import annotations

from pathlib import Path
from time import perf_counter
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.backend.schemas import ErrorResponse, FeedbackRequest, FeedbackResponse, PredictionRequest, PredictionResponse
from src.feedback.store import FeedbackRecord, FeedbackValidationError, append_feedback
from src.inference.champion import ChampionPredictor, InferenceError


app = FastAPI(title="LaLiga Prediction API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)
ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_PATH = ROOT / "data/feedback/predictions_feedback.csv"
_predictor: ChampionPredictor | None = None


def _error(request_id: str, code: str, message: str, *, details: list[dict] | None = None, status_code: int = 422) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ErrorResponse(request_id=request_id, error=code, message=message, details=details or []).model_dump())


def get_predictor() -> ChampionPredictor:
    global _predictor
    if _predictor is None:
        _predictor = ChampionPredictor(ROOT / "data/processed/laliga_matches_clean.csv", ROOT / "models/champion/laliga_champion_v1.joblib", ROOT / "reports/experiments/champion_metadata.json")
    return _predictor


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = str(uuid4())
    return _error(request_id, "INVALID_INPUT", "La entrada no cumple el contrato.", details=[{"field": ".".join(map(str, item["loc"][1:])), "reason": item["type"]} for item in exc.errors()])


@app.get("/health")
def health_check():
    return {"status": "ok", "model_loaded": _predictor is not None}


@app.post("/api/v1/predictions", response_model=PredictionResponse, responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
def create_prediction(payload: PredictionRequest):
    request_id = str(uuid4())
    started = perf_counter()
    try:
        result = get_predictor().predict(payload.home_team, payload.away_team, payload.match_date)
    except InferenceError as exc:
        return _error(request_id, exc.code, exc.message, status_code=exc.status_code)
    except Exception:
        return _error(request_id, "MODEL_UNAVAILABLE", "El Champion no está disponible.", status_code=503)
    return PredictionResponse(request_id=request_id, prediction=result["prediction"], probabilities={"H": result["H"], "D": result["D"], "A": result["A"]}, model_version=get_predictor().metadata["champion_model_version"], data_version=get_predictor().metadata["source_data_sha256"], latency_ms=(perf_counter() - started) * 1000, message="Estimación probabilística basada únicamente en el histórico anterior.")


@app.post("/api/v1/feedback", response_model=FeedbackResponse, responses={422: {"model": ErrorResponse}})
def create_feedback(payload: FeedbackRequest):
    request_id = str(uuid4())
    try:
        stored = append_feedback(
            FeedbackRecord(
                home_team=payload.home_team,
                away_team=payload.away_team,
                match_date=payload.match_date,
                actual_result=payload.actual_result,
                predicted_result=payload.predicted_result,
                model_version=payload.model_version,
                data_version=payload.data_version,
                comment=payload.comment,
            ),
            FEEDBACK_PATH,
        )
    except FeedbackValidationError as exc:
        return _error(request_id, "INVALID_FEEDBACK", str(exc))
    return FeedbackResponse(feedback_id=stored.feedback_id)
