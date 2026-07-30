from __future__ import annotations

from datetime import date

import pytest

from src.feedback.store import FeedbackRecord, FeedbackValidationError, append_feedback, load_feedback


def _valid_record(**overrides) -> FeedbackRecord:
    defaults = dict(
        home_team="Real Madrid",
        away_team="Barcelona",
        match_date=date(2026, 9, 10),
        actual_result="H",
        predicted_result="D",
        model_version="ensemble_abcd_soft_voting_v1",
        data_version="6288a872",
        comment="Buen partido",
    )
    defaults.update(overrides)
    return FeedbackRecord(**defaults)


def test_append_and_recover_feedback_round_trips(tmp_path) -> None:
    path = tmp_path / "feedback.csv"
    stored = append_feedback(_valid_record(), path)
    recovered = load_feedback(path)
    assert len(recovered) == 1
    assert recovered[0]["feedback_id"] == stored.feedback_id
    assert recovered[0]["home_team"] == "Real Madrid"
    assert recovered[0]["actual_result"] == "H"


def test_append_is_additive_and_never_overwrites(tmp_path) -> None:
    path = tmp_path / "feedback.csv"
    append_feedback(_valid_record(home_team="Real Madrid"), path)
    append_feedback(_valid_record(home_team="Sevilla", away_team="Betis"), path)
    recovered = load_feedback(path)
    assert len(recovered) == 2
    assert {row["home_team"] for row in recovered} == {"Real Madrid", "Sevilla"}


def test_rejects_same_team_as_home_and_away(tmp_path) -> None:
    with pytest.raises(FeedbackValidationError):
        append_feedback(_valid_record(home_team="Barcelona", away_team="Barcelona"), tmp_path / "feedback.csv")


def test_rejects_invalid_actual_result(tmp_path) -> None:
    with pytest.raises(FeedbackValidationError):
        append_feedback(_valid_record(actual_result="X"), tmp_path / "feedback.csv")


def test_rejects_invalid_predicted_result(tmp_path) -> None:
    with pytest.raises(FeedbackValidationError):
        append_feedback(_valid_record(predicted_result="X"), tmp_path / "feedback.csv")


def test_predicted_result_is_optional(tmp_path) -> None:
    path = tmp_path / "feedback.csv"
    append_feedback(_valid_record(predicted_result=None), path)
    recovered = load_feedback(path)
    assert recovered[0]["predicted_result"] == ""


def test_load_feedback_returns_empty_list_when_file_does_not_exist(tmp_path) -> None:
    assert load_feedback(tmp_path / "missing.csv") == []


def test_invalid_feedback_is_never_written_to_disk(tmp_path) -> None:
    path = tmp_path / "feedback.csv"
    with pytest.raises(FeedbackValidationError):
        append_feedback(_valid_record(actual_result="X"), path)
    assert not path.exists()
