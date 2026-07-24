from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class PredictionRequest(BaseModel):
    home_team: str
    away_team: str
    match_date: date


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
    prediction: Literal["H", "D", "A"]
    probabilities: ClassProbabilities
    model_version: str
    data_version: str
    status: Literal["ok"] = "ok"
    message: str
