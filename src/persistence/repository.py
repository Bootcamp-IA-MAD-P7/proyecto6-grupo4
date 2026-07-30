"""T-5.3: operaciones de escritura/lectura sobre las tablas persistidas."""

from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.persistence.models import FeedbackRecord, PredictionRecord, UserRecord


def create_user(
    session: Session,
    *,
    email: str,
    password_hash: str,
    first_name: str,
    last_name: str,
    birth_date: date,
    phone: str,
) -> UserRecord:
    record = UserRecord(
        email=email,
        password_hash=password_hash,
        first_name=first_name,
        last_name=last_name,
        birth_date=birth_date,
        phone=phone,
    )
    session.add(record)
    session.flush()
    return record


def get_user_by_email(session: Session, *, email: str) -> UserRecord | None:
    return session.scalars(select(UserRecord).where(UserRecord.email == email)).first()


def get_user_by_id(session: Session, *, user_id: str) -> UserRecord | None:
    return session.get(UserRecord, user_id)


def save_prediction(
    session: Session,
    *,
    request_id: str,
    user_id: str,
    home_team: str,
    away_team: str,
    match_date: date,
    prediction: str,
    probability_h: float,
    probability_d: float,
    probability_a: float,
    model_version: str,
    data_version: str,
    latency_ms: float,
) -> PredictionRecord:
    record = PredictionRecord(
        request_id=request_id,
        user_id=user_id,
        home_team=home_team,
        away_team=away_team,
        match_date=match_date,
        prediction=prediction,
        probability_h=probability_h,
        probability_d=probability_d,
        probability_a=probability_a,
        model_version=model_version,
        data_version=data_version,
        latency_ms=latency_ms,
    )
    session.add(record)
    session.flush()
    return record


def list_predictions_for_user(session: Session, *, user_id: str) -> list[PredictionRecord]:
    return list(
        session.scalars(
            select(PredictionRecord)
            .where(PredictionRecord.user_id == user_id)
            .order_by(PredictionRecord.created_at.desc())
        )
    )


def save_feedback(
    session: Session,
    *,
    feedback_id: str,
    home_team: str,
    away_team: str,
    match_date: date,
    actual_result: str,
    predicted_result: str | None = None,
    model_version: str | None = None,
    data_version: str | None = None,
    comment: str | None = None,
) -> FeedbackRecord:
    record = FeedbackRecord(
        feedback_id=feedback_id,
        home_team=home_team,
        away_team=away_team,
        match_date=match_date,
        actual_result=actual_result,
        predicted_result=predicted_result,
        model_version=model_version,
        data_version=data_version,
        comment=comment,
    )
    session.add(record)
    session.flush()
    return record


def list_predictions(session: Session) -> list[PredictionRecord]:
    return list(session.scalars(select(PredictionRecord).order_by(PredictionRecord.created_at)))


def list_feedback(session: Session) -> list[FeedbackRecord]:
    return list(session.scalars(select(FeedbackRecord).order_by(FeedbackRecord.received_at)))


def count_predictions(session: Session) -> int:
    return len(list_predictions(session))


def count_feedback(session: Session) -> int:
    return len(list_feedback(session))
