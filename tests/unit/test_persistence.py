from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import date

import pytest
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from src.persistence.db import get_database_url, get_engine, init_schema, reset_engine_for_testing, session_scope
from src.persistence.models import Base
from src.persistence.repository import (
    count_feedback,
    count_predictions,
    create_user,
    get_user_by_email,
    get_user_by_id,
    list_feedback,
    list_predictions,
    list_predictions_for_user,
    save_feedback,
    save_prediction,
)


def _user_kwargs(email: str, password_hash: str) -> dict:
    return {
        "email": email,
        "password_hash": password_hash,
        "first_name": "Ana",
        "last_name": "García",
        "birth_date": date(1990, 5, 20),
        "phone": "+34 600 123 456",
    }


@pytest.fixture()
def session():
    # SQLite en memoria: valida la logica del esquema y del repositorio sin
    # requerir un Postgres real (eso se verifica aparte, ver database_schema.md).
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db_session:
        yield db_session


def test_create_user_and_lookup_by_email_and_id(session) -> None:
    user = create_user(session, **_user_kwargs("fan@example.com", "hashed-value"))
    session.commit()
    assert get_user_by_email(session, email="fan@example.com").id == user.id
    assert get_user_by_id(session, user_id=user.id).email == "fan@example.com"
    assert get_user_by_email(session, email="nadie@example.com") is None


def test_user_email_is_unique(session) -> None:
    create_user(session, **_user_kwargs("dup@example.com", "h1"))
    session.commit()
    with pytest.raises(Exception):
        create_user(session, **_user_kwargs("dup@example.com", "h2"))
        session.commit()


def test_save_and_list_predictions_round_trips(session) -> None:
    user = create_user(session, **_user_kwargs("a@example.com", "h"))
    session.commit()
    save_prediction(
        session, request_id="req-1", user_id=user.id, home_team="Real Madrid", away_team="Barcelona", match_date=date(2026, 9, 10),
        prediction="H", probability_h=0.4, probability_d=0.3, probability_a=0.3,
        model_version="ensemble_abcd_soft_voting_v1", data_version="sha", latency_ms=12.5,
    )
    session.commit()
    predictions = list_predictions(session)
    assert len(predictions) == 1
    assert predictions[0].request_id == "req-1"
    assert predictions[0].prediction == "H"
    assert count_predictions(session) == 1


def test_list_predictions_for_user_only_returns_that_users_rows(session) -> None:
    user_a = create_user(session, **_user_kwargs("a2@example.com", "h"))
    user_b = create_user(session, **_user_kwargs("b2@example.com", "h"))
    session.commit()
    save_prediction(
        session, request_id="req-a", user_id=user_a.id, home_team="Sevilla", away_team="Betis", match_date=date(2026, 9, 10),
        prediction="D", probability_h=0.3, probability_d=0.4, probability_a=0.3,
        model_version="v1", data_version="sha", latency_ms=1.0,
    )
    save_prediction(
        session, request_id="req-b", user_id=user_b.id, home_team="Valencia", away_team="Celta", match_date=date(2026, 9, 11),
        prediction="A", probability_h=0.2, probability_d=0.3, probability_a=0.5,
        model_version="v1", data_version="sha", latency_ms=1.0,
    )
    session.commit()
    only_a = list_predictions_for_user(session, user_id=user_a.id)
    assert [p.request_id for p in only_a] == ["req-a"]


def test_save_and_list_feedback_round_trips(session) -> None:
    save_feedback(
        session, feedback_id="fb-1", home_team="Sevilla", away_team="Betis", match_date=date(2026, 9, 15),
        actual_result="D", predicted_result="H", model_version="ensemble_abcd_soft_voting_v1",
        data_version="sha", comment="Prueba",
    )
    session.commit()
    feedback = list_feedback(session)
    assert len(feedback) == 1
    assert feedback[0].feedback_id == "fb-1"
    assert feedback[0].actual_result == "D"
    assert count_feedback(session) == 1


def test_predictions_persist_across_new_sessions_on_the_same_engine() -> None:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    with factory() as first_session:
        user = create_user(first_session, **_user_kwargs("c@example.com", "h"))
        first_session.commit()
        save_prediction(
            first_session, request_id="req-2", user_id=user.id, home_team="Valencia", away_team="Celta", match_date=date(2026, 10, 1),
            prediction="A", probability_h=0.2, probability_d=0.3, probability_a=0.5,
            model_version="v1", data_version="sha", latency_ms=5.0,
        )
        first_session.commit()

    # Una sesion completamente nueva, como si fuera otro proceso/reinicio de la app,
    # debe seguir viendo los datos: la persistencia no depende de la sesion en memoria.
    with factory() as second_session:
        predictions = list_predictions(second_session)
        assert len(predictions) == 1
        assert predictions[0].request_id == "req-2"


def test_feedback_id_is_unique(session) -> None:
    save_feedback(
        session, feedback_id="fb-dup", home_team="A", away_team="B", match_date=date(2026, 1, 1), actual_result="H",
    )
    session.commit()
    with pytest.raises(Exception):
        save_feedback(
            session, feedback_id="fb-dup", home_team="C", away_team="D", match_date=date(2026, 1, 2), actual_result="A",
        )


def test_sqlite_memory_fallback_shares_schema_and_data_across_threads(monkeypatch) -> None:
    # Reproduce el escenario real de FastAPI: endpoints sincronos corren en
    # un threadpool, así que distintas peticiones pueden caer en hilos
    # distintos. Sin poolclass=StaticPool, cada hilo vería una base
    # ``:memory:`` vacía y fallaría con "no such table".
    monkeypatch.delenv("DATABASE_URL", raising=False)
    reset_engine_for_testing()
    try:
        init_schema(get_engine())
        with session_scope() as session:
            user_id = create_user(session, **_user_kwargs("thread@example.com", "h")).id

        def save_from_this_thread() -> None:
            with session_scope() as session:
                save_prediction(
                    session, request_id="req-thread", user_id=user_id, home_team="Alaves", away_team="Girona",
                    match_date=date(2026, 11, 1), prediction="D", probability_h=0.3, probability_d=0.4,
                    probability_a=0.3, model_version="v1", data_version="sha", latency_ms=1.0,
                )

        with ThreadPoolExecutor(max_workers=1) as executor:
            executor.submit(save_from_this_thread).result()

        with session_scope() as session:
            assert count_predictions(session) == 1
    finally:
        reset_engine_for_testing()


def test_init_schema_adds_user_id_to_a_predictions_table_created_before_auth() -> None:
    # Regresion real, encontrada probando contra un Postgres con datos ya
    # existentes (volumen Docker reutilizado): create_all() NO altera una
    # tabla que ya existe, asi que una "predictions" creada antes de T-6.1
    # (autenticacion) se quedaba sin la columna user_id nueva. init_schema()
    # debe migrarla de forma idempotente sin tocar las filas existentes.
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    with engine.begin() as connection:
        connection.execute(text(
            "CREATE TABLE predictions ("
            "id VARCHAR(36) PRIMARY KEY, request_id VARCHAR(36) NOT NULL, "
            "home_team VARCHAR(80) NOT NULL, away_team VARCHAR(80) NOT NULL, "
            "match_date DATE NOT NULL, prediction VARCHAR(1) NOT NULL, "
            "probability_h FLOAT NOT NULL, probability_d FLOAT NOT NULL, probability_a FLOAT NOT NULL, "
            "model_version VARCHAR(120) NOT NULL, data_version VARCHAR(120) NOT NULL, "
            "latency_ms FLOAT NOT NULL, created_at DATETIME NOT NULL)"
        ))
        connection.execute(text(
            "INSERT INTO predictions VALUES ('id-1', 'req-1', 'Sevilla', 'Betis', '2026-01-01', 'H', "
            "0.4, 0.3, 0.3, 'v1', 'sha', 1.0, '2026-01-01 00:00:00')"
        ))

    init_schema(engine)

    columns = {column["name"] for column in inspect(engine).get_columns("predictions")}
    assert "user_id" in columns
    with engine.connect() as connection:
        row = connection.execute(text("SELECT request_id, user_id FROM predictions")).first()
    assert row.request_id == "req-1"
    assert row.user_id is None

    # Idempotente: correrlo de nuevo no debe fallar ni duplicar la columna.
    init_schema(engine)


def test_render_postgres_url_uses_the_installed_psycopg_driver(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:password@internal-host:5432/laliga",
    )

    assert (
        get_database_url()
        == "postgresql+psycopg://user:password@internal-host:5432/laliga"
    )
