"""T-5.3: esquema de las tablas persistidas (PostgreSQL vía SQLAlchemy).

Documentado también en `docs/database_schema.md`. Cambiar una columna aquí
sin actualizar ese documento se considera incompleto.
"""

from __future__ import annotations

from datetime import UTC, date, datetime
from uuid import uuid4

from sqlalchemy import Date, DateTime, Float, ForeignKey, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class UserRecord(Base):
    """Un usuario registrado. La contraseña nunca se guarda en texto plano."""

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(120), nullable=False)
    last_name: Mapped[str] = mapped_column(String(120), nullable=False)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class PredictionRecord(Base):
    """Una fila por cada predicción servida por `/api/v1/predictions`."""

    __tablename__ = "predictions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    request_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    # Nullable a nivel de esquema por compatibilidad con filas de antes de
    # T-6.1 (autenticación), que no tenían usuario asociado. La aplicación
    # siempre provee user_id para predicciones nuevas (login obligatorio).
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("users.id"), nullable=True, index=True)
    home_team: Mapped[str] = mapped_column(String(80), nullable=False)
    away_team: Mapped[str] = mapped_column(String(80), nullable=False)
    match_date: Mapped[date] = mapped_column(Date, nullable=False)
    prediction: Mapped[str] = mapped_column(String(1), nullable=False)
    probability_h: Mapped[float] = mapped_column(Float, nullable=False)
    probability_d: Mapped[float] = mapped_column(Float, nullable=False)
    probability_a: Mapped[float] = mapped_column(Float, nullable=False)
    model_version: Mapped[str] = mapped_column(String(120), nullable=False)
    data_version: Mapped[str] = mapped_column(String(120), nullable=False)
    latency_ms: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)


class FeedbackRecord(Base):
    """Una fila por cada feedback recibido en `/api/v1/feedback`.

    Mismo contrato que `src/feedback/store.py` (T-4.3); esta tabla es la
    persistencia durable, la CSV sigue existiendo como registro append-only
    adicional sin infraestructura.
    """

    __tablename__ = "feedback"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    feedback_id: Mapped[str] = mapped_column(String(36), nullable=False, unique=True, index=True)
    home_team: Mapped[str] = mapped_column(String(80), nullable=False)
    away_team: Mapped[str] = mapped_column(String(80), nullable=False)
    match_date: Mapped[date] = mapped_column(Date, nullable=False)
    predicted_result: Mapped[str | None] = mapped_column(String(1), nullable=True)
    actual_result: Mapped[str] = mapped_column(String(1), nullable=False)
    model_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    data_version: Mapped[str | None] = mapped_column(String(120), nullable=True)
    comment: Mapped[str | None] = mapped_column(String(500), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(UTC), nullable=False)
