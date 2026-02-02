from dataclasses import dataclass

from pydantic import BaseModel

@dataclass
class TraitVector(BaseModel):
    extroversion: int = 5
    agreeableness: int = 5
    conscientiousness: int = 5
    neuroticism: int = 5
    openness: int = 5
    dominance: int = 5
    empathy: int = 5
    risk_taking: int = 5
    emotional_stability: int = 5
    self_control: int = 5
