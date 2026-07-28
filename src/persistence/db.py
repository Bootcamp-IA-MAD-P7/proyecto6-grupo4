"""T-5.3: conexión a PostgreSQL, configurable por `DATABASE_URL`.

Sin `DATABASE_URL` (por ejemplo en tests unitarios o en un entorno sin
Postgres disponible), `get_engine()` usa SQLite en memoria: el esquema y
las consultas son idénticos porque SQLAlchemy abstrae el dialecto, pero la
persistencia real solo ocurre con Postgres configurado.
"""

from __future__ import annotations

import os
from contextlib import contextmanager

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.persistence.models import Base

DEFAULT_LOCAL_DATABASE_URL = "postgresql+psycopg://laliga:laliga@localhost:5432/laliga"
_engine: Engine | None = None
_session_factory: sessionmaker[Session] | None = None


def get_database_url() -> str:
    return os.environ.get("DATABASE_URL", "sqlite:///:memory:")


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        url = get_database_url()
        connect_args = {"check_same_thread": False} if url.startswith("sqlite") else {}
        _engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    return _engine


def init_schema(engine: Engine | None = None) -> None:
    """Crea las tablas si no existen. Idempotente: seguro de llamar en cada arranque."""

    Base.metadata.create_all(engine or get_engine())


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
