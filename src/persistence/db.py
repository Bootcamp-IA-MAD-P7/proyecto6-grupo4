"""T-5.3: conexión a PostgreSQL, configurable por `DATABASE_URL`.

Sin `DATABASE_URL` (por ejemplo en tests unitarios o en un entorno sin
Postgres disponible), `get_engine()` usa SQLite en memoria: el esquema y
las consultas son idénticos porque SQLAlchemy abstrae el dialecto, pero la
persistencia real solo ocurre con Postgres configurado.

SQLite en memoria requiere `poolclass=StaticPool`: por defecto SQLAlchemy
abre una conexión (y por tanto una base ``:memory:`` distinta) por hilo, y
FastAPI ejecuta los endpoints síncronos en un threadpool. Sin StaticPool,
una petición puede caer en un hilo cuya base en memoria nunca vio
`init_schema()`, resultando en ``sqlite3.OperationalError: no such table``.
StaticPool fuerza que todos los hilos compartan la misma conexión/base.
"""

from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from src.persistence.models import Base

DEFAULT_LOCAL_DATABASE_URL = "postgresql+psycopg://laliga:laliga@localhost:5432/laliga"
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_database_url() -> str:
    url = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = get_database_url()
        if url.startswith("sqlite"):
            _engine = create_engine(
                url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                pool_pre_ping=True,
            )
        else:
            _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def init_schema(engine: Engine | None = None) -> None:
    """Crea las tablas si no existen. Idempotente: seguro de llamar en cada arranque.

    `create_all()` solo crea tablas que no existen; NO altera una tabla ya
    existente para añadirle una columna nueva (por ejemplo `predictions.user_id`,
    añadido en T-6.1 sobre una base que ya tenía filas de antes de la
    autenticación). Se aplica una migración mínima e idempotente para ese
    caso puntual; una evolución de esquema más compleja debería pasar a
    Alembic, fuera del alcance de T-5.3/T-6.1.
    """

    target_engine = engine or get_engine()
    Base.metadata.create_all(target_engine)
    _ensure_predictions_user_id_column(target_engine)


def _ensure_predictions_user_id_column(engine: Engine) -> None:
    inspector = inspect(engine)
    if "predictions" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("predictions")}
    if "user_id" in columns:
        return
    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE predictions ADD COLUMN user_id VARCHAR(36)"))


def get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(bind=get_engine(), expire_on_commit=False)
    return _session_factory


@contextmanager
def session_scope():
    session = get_session_factory()()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def reset_engine_for_testing() -> None:
    """Fuerza recrear el engine/sessionmaker; solo para tests que cambian DATABASE_URL."""

    global _engine, _session_factory
    _engine = None
    _session_factory = None
