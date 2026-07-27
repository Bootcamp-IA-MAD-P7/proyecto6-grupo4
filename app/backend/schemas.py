from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


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
