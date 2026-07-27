"""T-4.3: almacenamiento append-only, validado y recuperable del feedback.

No depende de una base de datos (eso es T-5.3): usa un CSV append-only bajo
`data/feedback/`, con un esquema fijo y validación explícita antes de
escribir. `load_feedback` permite recuperar exactamente lo escrito, fila a
fila, para auditoría o para alimentar T-4.4/T-6.3 más adelante.
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

VALID_RESULTS = {"H", "D", "A"}

FEEDBACK_FIELDS = (
    "feedback_id",
    "received_at",
    "home_team",
    "away_team",
    "match_date",
    "predicted_result",
    "actual_result",
    "model_version",
    "data_version",
    "comment",
)


class FeedbackValidationError(ValueError):
    """Feedback que no cumple el contrato mínimo; nunca se escribe a disco."""


@dataclass(frozen=True)
class FeedbackRecord:
    home_team: str
    away_team: str
    match_date: date
    actual_result: str
    predicted_result: str | None = None
    model_version: str | None = None
    data_version: str | None = None
    comment: str | None = None
    feedback_id: str | None = None
    received_at: str | None = None

    def validated(self) -> "FeedbackRecord":
        errors: list[str] = []
        if not self.home_team or not self.home_team.strip():
            errors.append("home_team no puede estar vacío.")
        if not self.away_team or not self.away_team.strip():
            errors.append("away_team no puede estar vacío.")
        if self.home_team.strip().casefold() == self.away_team.strip().casefold():
            errors.append("home_team y away_team deben ser distintos.")
        if self.actual_result not in VALID_RESULTS:
            errors.append(f"actual_result debe ser uno de {sorted(VALID_RESULTS)}.")
        if self.predicted_result is not None and self.predicted_result not in VALID_RESULTS:
            errors.append(f"predicted_result debe ser uno de {sorted(VALID_RESULTS)} o vacío.")
        if self.comment is not None and len(self.comment) > 500:
            errors.append("comment no puede superar 500 caracteres.")
        if errors:
            raise FeedbackValidationError("; ".join(errors))
        return FeedbackRecord(
            home_team=self.home_team.strip(),
            away_team=self.away_team.strip(),
            match_date=self.match_date,
            actual_result=self.actual_result,
            predicted_result=self.predicted_result,
            model_version=self.model_version,
            data_version=self.data_version,
            comment=self.comment.strip() if self.comment else None,
            feedback_id=self.feedback_id or str(uuid4()),
            received_at=self.received_at or datetime.now(UTC).isoformat(),
        )

    def as_row(self) -> dict[str, str]:
        row = asdict(self)
        row["match_date"] = self.match_date.isoformat()
        return {key: ("" if row[key] is None else str(row[key])) for key in FEEDBACK_FIELDS}


def append_feedback(record: FeedbackRecord, path: str | Path) -> FeedbackRecord:
    """Valida y añade una fila; nunca sobrescribe filas existentes."""

    validated = record.validated()
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    is_new_file = not file_path.exists() or file_path.stat().st_size == 0
    with file_path.open("a", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=FEEDBACK_FIELDS)
        if is_new_file:
            writer.writeheader()
        writer.writerow(validated.as_row())
    return validated


def load_feedback(path: str | Path) -> list[dict[str, Any]]:
    """Recupera todo el feedback almacenado, fila a fila, sin transformarlo."""

    file_path = Path(path)
    if not file_path.exists():
        return []
    with file_path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))
