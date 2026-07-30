from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from time import perf_counter
from typing import AsyncIterator
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.backend.schemas import ErrorResponse, FeedbackRequest, FeedbackResponse, PredictionRequest, PredictionResponse
from src.feedback.store import FeedbackRecord, FeedbackValidationError, append_feedback
from src.inference.champion import ChampionPredictor, InferenceError
from src.persistence.db import init_schema, session_scope
from src.persistence import repository as persistence_repository


logger = logging.getLogger("laliga.backend")
logger.setLevel(logging.INFO)
if not logging.getLogger().handlers:
    # Sin esto, logger.info() queda silenciado por el "handler of last
    # resort" de Python (que solo muestra WARNING+): el log estructurado
    # por peticion (request_id/ruta/estado/latencia) nunca se veria.
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

ROOT = Path(__file__).resolve().parents[2]
FEEDBACK_PATH = ROOT / "data/feedback/predictions_feedback.csv"
_predictor: ChampionPredictor | None = None


def get_predictor() -> ChampionPredictor:
    global _predictor
    if _predictor is None:
        _predictor = ChampionPredictor(ROOT / "data/processed/laliga_matches_clean.csv", ROOT / "models/champion/laliga_champion_v1.joblib", ROOT / "reports/experiments/champion_metadata.json")
    return _predictor


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        init_schema()
    except Exception:
        logger.exception("No se pudo inicializar el esquema de persistencia; la API sigue disponible.")
    try:
        get_predictor()
    except Exception:
        logger.exception("El Champion no superó la validación de arranque.")
    yield


MAX_PAYLOAD_BYTES = 4096


app = FastAPI(title="LaLiga Prediction API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type"],
)


@app.middleware("http")
async def request_id_size_limit_and_logging(request: Request, call_next):
    """Asigna request_id, rechaza payloads > 4 KiB y deja un log estructurado por petición.

    El log nunca incluye el cuerpo de la petición, solo metadatos (RNF-06).
    """

    request.state.request_id = str(uuid4())
    started = perf_counter()

    content_length = request.headers.get("content-length")
    if content_length is not None:
        try:
            too_large = int(content_length) > MAX_PAYLOAD_BYTES
        except ValueError:
            too_large = False
        if too_large:
            response = _error(
                request.state.request_id,
                "PAYLOAD_TOO_LARGE",
                "El cuerpo supera 4 KiB.",
                status_code=413,
            )
            _log_request(request, response.status_code, started)
            return response

    response = await call_next(request)
    _log_request(request, response.status_code, started)
    return response


def _log_request(request: Request, status_code: int, started: float) -> None:
    latency_ms = (perf_counter() - started) * 1000
    model_version = _predictor.metadata.get("champion_model_version") if _predictor else None
    logger.info(
        "request_id=%s method=%s path=%s status=%s latency_ms=%.2f model_version=%s",
        request.state.request_id, request.method, request.url.path, status_code, latency_ms, model_version,
    )


def _persist_prediction_best_effort(**kwargs) -> None:
    try:
        with session_scope() as session:
            persistence_repository.save_prediction(session, **kwargs)
    except Exception:
        logger.exception("No se pudo persistir la predicción; la respuesta al cliente no se ve afectada.")


def _persist_feedback_best_effort(**kwargs) -> None:
    try:
        with session_scope() as session:
            persistence_repository.save_feedback(session, **kwargs)
    except Exception:
        logger.exception("No se pudo persistir el feedback en la base de datos; el CSV local sigue siendo la fuente recuperable.")


def _error(request_id: str, code: str, message: str, *, details: list[dict] | None = None, status_code: int = 422) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=ErrorResponse(request_id=request_id, error=code, message=message, details=details or []).model_dump())


@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    errors = exc.errors()
    if any(error["type"] == "json_invalid" for error in errors):
        return _error(request_id, "MALFORMED_JSON", "El cuerpo no es JSON válido.", status_code=400)
    return _error(request_id, "INVALID_INPUT", "La entrada no cumple el contrato.", details=[{"field": ".".join(map(str, item["loc"][1:])), "reason": item["type"]} for item in errors])


@app.get("/health")
def health_check():
    try:
        predictor = get_predictor()
    except Exception:
        return JSONResponse(
            status_code=503,
            content={"status": "error", "model_loaded": False},
        )
    return {
        "status": "ok",
        "model_loaded": True,
        "model_version": predictor.metadata["champion_model_version"],
    }


@app.post("/api/v1/predictions", response_model=PredictionResponse, responses={404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
def create_prediction(payload: PredictionRequest, request: Request):
    request_id = request.state.request_id
    started = perf_counter()
    try:
        result = get_predictor().predict(payload.home_team, payload.away_team, payload.match_date)
    except InferenceError as exc:
        return _error(request_id, exc.code, exc.message, status_code=exc.status_code)
    except Exception:
        return _error(request_id, "MODEL_UNAVAILABLE", "El Champion no está disponible.", status_code=503)
    latency_ms = (perf_counter() - started) * 1000
    model_version = get_predictor().metadata["champion_model_version"]
    data_version = get_predictor().metadata["source_data_sha256"]
    _persist_prediction_best_effort(
        request_id=request_id, home_team=payload.home_team, away_team=payload.away_team, match_date=payload.match_date,
        prediction=result["prediction"], probability_h=result["H"], probability_d=result["D"], probability_a=result["A"],
        model_version=model_version, data_version=data_version, latency_ms=latency_ms,
    )
    return PredictionResponse(request_id=request_id, prediction=result["prediction"], probabilities={"H": result["H"], "D": result["D"], "A": result["A"]}, model_version=model_version, data_version=data_version, latency_ms=latency_ms, message="Estimación probabilística basada únicamente en el histórico anterior.")


@app.post("/api/v1/feedback", response_model=FeedbackResponse, responses={422: {"model": ErrorResponse}})
def create_feedback(payload: FeedbackRequest, request: Request):
    request_id = request.state.request_id
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
    _persist_feedback_best_effort(
        feedback_id=stored.feedback_id, home_team=stored.home_team, away_team=stored.away_team, match_date=stored.match_date,
        actual_result=stored.actual_result, predicted_result=stored.predicted_result, model_version=stored.model_version,
        data_version=stored.data_version, comment=stored.comment,
    )
    return FeedbackResponse(feedback_id=stored.feedback_id)


FRONTEND_PATH = ROOT / "app/frontend/public"
if FRONTEND_PATH.exists():
    app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
