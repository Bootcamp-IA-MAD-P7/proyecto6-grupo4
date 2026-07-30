import re
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

_EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=8, max_length=72)

    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        if not _EMAIL_PATTERN.match(value):
            raise ValueError("El email no tiene un formato válido.")
        return value.lower()


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
