import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_PATTERN = re.compile(r"^\+?[0-9 ()-]{6,30}$")
MIN_REGISTRATION_AGE = 18


class PredictionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    home_team: str = Field(min_length=1, max_length=80)
    away_team: str = Field(min_length=1, max_length=80)
    match_date: date

    @model_validator(mode="after")
    def different_teams(self):
        if self.home_team.casefold() == self.away_team.casefold():
            raise ValueError("Los equipos local y visitante deben ser distintos.")
        return self


class ClassProbabilities(BaseModel):
    H: float = Field(ge=0, le=1)
    D: float = Field(ge=0, le=1)
    A: float = Field(ge=0, le=1)

    @model_validator(mode="after")
    def probabilities_sum_to_one(self):
        total = self.H + self.D + self.A
        if abs(total - 1.0) > 1e-6:
            raise ValueError("H, D and A probabilities must sum to 1")
        return self


class PredictionResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    request_id: str
    prediction: Literal["H", "D", "A"]
    probabilities: ClassProbabilities
    model_version: str
    data_version: str
    status: Literal["ok"] = "ok"
    latency_ms: float = Field(ge=0)
    message: str


class FeedbackRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    home_team: str = Field(min_length=1, max_length=80)
    away_team: str = Field(min_length=1, max_length=80)
    match_date: date
    actual_result: Literal["H", "D", "A"]
    predicted_result: Literal["H", "D", "A"] | None = None
    model_version: str | None = Field(default=None, max_length=120)
    data_version: str | None = Field(default=None, max_length=120)
    comment: str | None = Field(default=None, max_length=500)

    @model_validator(mode="after")
    def different_teams(self):
        if self.home_team.casefold() == self.away_team.casefold():
            raise ValueError("Los equipos local y visitante deben ser distintos.")
        return self


class FeedbackResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    feedback_id: str
    status: Literal["ok"] = "ok"
    message: str = "Feedback registrado."


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    first_name: str = Field(min_length=1, max_length=120)
    last_name: str = Field(min_length=1, max_length=120)
    birth_date: date
    phone: str = Field(min_length=6, max_length=30)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)
    accepts_terms: bool = Field(description="Confirma ser mayor de 18 años y que los datos son correctos.")

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if not _EMAIL_PATTERN.match(value):
            raise ValueError("El email no tiene un formato válido.")
        return value.lower()

    @field_validator("phone")
    @classmethod
    def valid_phone(cls, value: str) -> str:
        if not _PHONE_PATTERN.match(value):
            raise ValueError("El teléfono no tiene un formato válido.")
        return value

    @field_validator("accepts_terms")
    @classmethod
    def must_accept_terms(cls, value: bool) -> bool:
        if not value:
            raise ValueError("Debes confirmar que eres mayor de 18 años y que los datos son correctos.")
        return value

    @model_validator(mode="after")
    def must_be_adult(self):
        today = date.today()
        age = today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        if self.birth_date > today:
            raise ValueError("La fecha de nacimiento no puede ser futura.")
        if age < MIN_REGISTRATION_AGE:
            raise ValueError("Debes ser mayor de 18 años para registrarte.")
        return self


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=72)

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.lower()


class UserSummary(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str


class AuthResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    status: Literal["ok"] = "ok"
    access_token: str
    token_type: Literal["bearer"] = "bearer"
    user: UserSummary


class PredictionHistoryItem(BaseModel):
    request_id: str
    home_team: str
    away_team: str
    match_date: date
    prediction: Literal["H", "D", "A"]
    probabilities: ClassProbabilities
    model_version: str
    data_version: str
    created_at: datetime


class HistoryResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    status: Literal["ok"] = "ok"
    items: list[PredictionHistoryItem]


class TeamSummary(BaseModel):
    value: str
    label: str


class TeamsResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    status: Literal["ok"] = "ok"
    items: list[TeamSummary]


class FixtureItem(BaseModel):
    date: date
    time: str
    home_team: str
    home_label: str
    away_team: str
    away_label: str
    venue: str
    city: str
    has_history: bool


class FixturesResponse(BaseModel):
    contract_version: Literal["1.0"] = "1.0"
    status: Literal["ok"] = "ok"
    items: list[FixtureItem]


class ErrorDetail(BaseModel):
    field: str | None = None
    reason: str


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    contract_version: Literal["1.0"] = "1.0"
    request_id: str
    error: str
    message: str
    details: list[ErrorDetail] = []
