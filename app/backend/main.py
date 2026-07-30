from __future__ import annotations

import logging
import os
import time
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path
from time import perf_counter
from typing import AsyncIterator
from uuid import uuid4

from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.backend import fixtures as fixtures_catalog
from app.backend.dependencies import AuthenticatedUser, require_current_user
from app.backend.schemas import (
    AuthResponse,
    ErrorResponse,
    FeedbackRequest,
    FeedbackResponse,
    FixturesResponse,
    HistoryResponse,
    LoginRequest,
    PredictionHistoryItem,
    PredictionRequest,
    PredictionResponse,
    RegisterRequest,
    RefreshTokenRequest,
    TeamsResponse,
    UserSummary,
)
from src.auth.errors import AuthError
from src.auth.security import hash_password, verify_password
from src.auth.tokens import create_access_token, create_refresh_token, decode_access_token
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

# --- Rate limiter simple (in-memory, por IP) ---
_rate_limit_store: dict[str, list[float]] = defaultdict(list)
RATE_LIMIT_WINDOW = 60  # segundos
RATE_LIMIT_MAX_AUTH = 10  # intentos por ventana


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    _rate_limit_store[ip] = [t for t in _rate_limit_store[ip] if now - t < RATE_LIMIT_WINDOW]
    if len(_rate_limit_store[ip]) >= RATE_LIMIT_MAX_AUTH:
        return False
    _rate_limit_store[ip].append(now)
    return True


app = FastAPI(title="LaLiga Prediction API", version="0.1.0", lifespan=lifespan)

_cors_origins = os.environ.get("CORS_ORIGINS", "*")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _cors_origins.split(",")],
    allow_methods=["POST", "GET"],
    allow_headers=["Content-Type", "Authorization"],
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


@app.exception_handler(AuthError)
async def auth_error(request: Request, exc: AuthError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", str(uuid4()))
    return _error(request_id, exc.code, exc.message, status_code=exc.status_code)


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


@app.post("/api/v1/auth/register", response_model=AuthResponse, responses={409: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
def register(payload: RegisterRequest, request: Request):
    request_id = request.state.request_id
    ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(ip):
        return _error(request_id, "RATE_LIMITED", "Demasiadas peticiones. Espera un momento.", status_code=429)
    try:
        with session_scope() as session:
            if persistence_repository.get_user_by_email(session, email=payload.email) is not None:
                raise AuthError("EMAIL_ALREADY_REGISTERED", "Ya existe una cuenta con ese email.", 409)
            user = persistence_repository.create_user(
                session,
                email=payload.email,
                password_hash=hash_password(payload.password),
                first_name=payload.first_name,
                last_name=payload.last_name,
                birth_date=payload.birth_date,
                phone=payload.phone,
            )
            user_id, user_email, first_name, last_name = user.id, user.email, user.first_name, user.last_name
    except AuthError:
        raise
    except Exception:
        logger.exception("No se pudo registrar el usuario (base de datos no disponible).")
        return _error(request_id, "AUTH_UNAVAILABLE", "No se pudo completar el registro. Intenta de nuevo.", status_code=503)
    token = create_access_token(user_id=user_id, email=user_email)
    refresh = create_refresh_token(user_id=user_id, email=user_email)
    return AuthResponse(access_token=token, refresh_token=refresh, user=UserSummary(id=user_id, email=user_email, first_name=first_name, last_name=last_name))


@app.post("/api/v1/auth/login", response_model=AuthResponse, responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
def login(payload: LoginRequest, request: Request):
    request_id = request.state.request_id
    ip = request.client.host if request.client else "unknown"
    if not _check_rate_limit(ip):
        return _error(request_id, "RATE_LIMITED", "Demasiadas peticiones. Espera un momento.", status_code=429)
    try:
        with session_scope() as session:
            user = persistence_repository.get_user_by_email(session, email=payload.email)
            valid = user is not None and verify_password(payload.password, user.password_hash)
            if not valid:
                raise AuthError("INVALID_CREDENTIALS", "Email o contraseña incorrectos.", 401)
            user_id, user_email, first_name, last_name = user.id, user.email, user.first_name, user.last_name
    except AuthError:
        raise
    except Exception:
        logger.exception("No se pudo iniciar sesión (base de datos no disponible).")
        return _error(request_id, "AUTH_UNAVAILABLE", "No se pudo iniciar sesión. Intenta de nuevo.", status_code=503)
    token = create_access_token(user_id=user_id, email=user_email)
    refresh = create_refresh_token(user_id=user_id, email=user_email)
    return AuthResponse(access_token=token, refresh_token=refresh, user=UserSummary(id=user_id, email=user_email, first_name=first_name, last_name=last_name))


@app.post("/api/v1/auth/refresh", response_model=AuthResponse, responses={401: {"model": ErrorResponse}})
def refresh_token(payload: RefreshTokenRequest, request: Request):
    request_id = request.state.request_id
    try:
        data = decode_access_token(payload.refresh_token)
    except Exception:
        return _error(request_id, "UNAUTHORIZED", "El refresh token no es válido o expiró.", status_code=401)
    if data.get("type") != "refresh":
        return _error(request_id, "UNAUTHORIZED", "El token no es un refresh token válido.", status_code=401)
    user_id, email = data["sub"], data["email"]
    try:
        with session_scope() as session:
            user = persistence_repository.get_user_by_id(session, user_id=user_id)
            if user is None:
                return _error(request_id, "UNAUTHORIZED", "El usuario ya no existe.", status_code=401)
    except Exception:
        return _error(request_id, "AUTH_UNAVAILABLE", "No se pudo verificar la sesión.", status_code=503)
    new_access = create_access_token(user_id=user_id, email=email)
    new_refresh = create_refresh_token(user_id=user_id, email=email)
    return AuthResponse(
        access_token=new_access,
        refresh_token=new_refresh,
        user=UserSummary(id=user_id, email=email, first_name=user.first_name, last_name=user.last_name),
    )


@app.get("/api/v1/history", response_model=HistoryResponse, responses={401: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
def get_history(
    request: Request,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: AuthenticatedUser = Depends(require_current_user),
):
    request_id = request.state.request_id
    try:
        with session_scope() as session:
            records = persistence_repository.list_predictions_for_user(
                session, user_id=current_user.id, limit=limit, offset=offset,
            )
            items = [
                PredictionHistoryItem(
                    request_id=r.request_id, home_team=r.home_team, away_team=r.away_team, match_date=r.match_date,
                    prediction=r.prediction, probabilities={"H": r.probability_h, "D": r.probability_d, "A": r.probability_a},
                    model_version=r.model_version, data_version=r.data_version, created_at=r.created_at,
                )
                for r in records
            ]
    except Exception:
        logger.exception("No se pudo leer el historial (base de datos no disponible).")
        return _error(request_id, "HISTORY_UNAVAILABLE", "No se pudo cargar el historial. Intenta de nuevo.", status_code=503)
    return HistoryResponse(items=items)


@app.post("/api/v1/predictions", response_model=PredictionResponse, responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}, 409: {"model": ErrorResponse}, 503: {"model": ErrorResponse}})
def create_prediction(payload: PredictionRequest, request: Request, current_user: AuthenticatedUser = Depends(require_current_user)):
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
        request_id=request_id, user_id=current_user.id, home_team=payload.home_team, away_team=payload.away_team, match_date=payload.match_date,
        prediction=result["prediction"], probability_h=result["H"], probability_d=result["D"], probability_a=result["A"],
        model_version=model_version, data_version=data_version, latency_ms=latency_ms,
    )
    return PredictionResponse(request_id=request_id, prediction=result["prediction"], probabilities={"H": result["H"], "D": result["D"], "A": result["A"]}, model_version=model_version, data_version=data_version, latency_ms=latency_ms, message="Estimación probabilística basada únicamente en el histórico anterior.")


@app.post("/api/v1/feedback", response_model=FeedbackResponse, responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}})
def create_feedback(payload: FeedbackRequest, request: Request, current_user: AuthenticatedUser = Depends(require_current_user)):
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


@app.get("/api/v1/teams", response_model=TeamsResponse)
def list_teams():
    return TeamsResponse(items=fixtures_catalog.list_teams())


@app.get("/api/v1/fixtures", response_model=FixturesResponse)
def list_fixtures(
    team: str | None = Query(default=None, description="Filtra por equipo (valor del catálogo, no el nombre visible)."),
    days: int = Query(default=30, ge=1, le=365, description="Ventana de días desde hoy (ignorado si se pasa `team`)."),
):
    today = date.today()
    if team:
        items = fixtures_catalog.fixtures_for_team(team=team, today=today)
    else:
        items = fixtures_catalog.upcoming_fixtures(today=today, days=days)
    return FixturesResponse(items=items)


REACT_DIST = ROOT / "app/frontend-react/dist"
if REACT_DIST.exists():
    app.mount("/", StaticFiles(directory=REACT_DIST, html=True), name="frontend")
