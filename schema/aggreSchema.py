from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict
from typing import Optional


class AggregationRequest(BaseModel):
    user: str


class AggregationResponse(BaseModel):
    user: str
    summary: Optional[str]

    extroversion: int
    agreeableness: int
    conscientiousness: int
    neuroticism: int
    openness: int
    dominance: int
    empathy: int
    risk_taking: int
    emotional_stability: int
    self_control: int

    model_config = ConfigDict(from_attributes=True)
