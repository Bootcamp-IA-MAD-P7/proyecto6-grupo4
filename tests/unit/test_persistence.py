from __future__ import annotations

from datetime import date

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.persistence.db import get_database_url
from src.persistence.models import Base
from src.persistence.repository import (
    count_feedback,
    count_predictions,
    list_feedback,
    list_predictions,
    save_feedback,
    save_prediction,
)


@pytest.fixture()
def session():
    # SQLite en memoria: valida la logica del esquema y del repositorio sin
    # requerir un Postgres real (eso se verifica aparte, ver database_schema.md).
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db_session:
        yield db_session


def test_save_and_list_predictions_round_trips(session) -> None:
    save_prediction(
        session, request_id="req-1", home_team="Real Madrid", away_team="Barcelona", match_date=date(2026, 9, 10),
        prediction="H", probability_h=0.4, probability_d=0.3, probability_a=0.3,
        model_version="ensemble_abcd_soft_voting_v1", data_version="sha", latency_ms=12.5,
    )
    session.commit()
    predictions = list_predictions(session)
    assert len(predictions) == 1
    assert predictions[0].request_id == "req-1"
    assert predictions[0].prediction == "H"
    assert count_predictions(session) == 1


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
        save_prediction(
            first_session, request_id="req-2", home_team="Valencia", away_team="Celta", match_date=date(2026, 10, 1),
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


def test_render_postgres_url_uses_the_installed_psycopg_driver(monkeypatch) -> None:
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://user:password@internal-host:5432/laliga",
    )

    assert (
        get_database_url()
        == "postgresql+psycopg://user:password@internal-host:5432/laliga"
    )
