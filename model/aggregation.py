from dataclasses import dataclass

from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from model.reflection import ReflectionModel
from model.trait_vector import TraitVector
from core.db.database import Base


@dataclass
class AggregationModel(Base):
    __tablename__ = "aggregation"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(64), nullable=False)

    extroversion = Column(Integer, nullable=False)
    agreeableness = Column(Integer, nullable=False)
    conscientiousness = Column(Integer, nullable=False)
    neuroticism = Column(Integer, nullable=False)
    openness = Column(Integer, nullable=False)
    dominance = Column(Integer, nullable=False)
    empathy = Column(Integer, nullable=False)
    risk_taking = Column(Integer, nullable=False)
    emotional_stability = Column(Integer, nullable=False)
    self_control = Column(Integer, nullable=False)

    summary = Column(Text)
    created_at = Column(TIMESTAMP, server_default=func.now())

    @property
    def personality(self) -> TraitVector:
        return TraitVector(
            self.extroversion,
            self.agreeableness,
            self.conscientiousness,
            self.neuroticism,
            self.openness,
            self.dominance,
            self.empathy,
            self.risk_taking,
            self.emotional_stability,
            self.self_control,
        )

    @staticmethod
    def from_reflection(
            reflection: ReflectionModel,
            traits: TraitVector,
    ) -> 'AggregationModel':
        return AggregationModel(
            user=reflection.user,
            summary=reflection.summary,

            extroversion=traits.extroversion,
            agreeableness=traits.agreeableness,
            conscientiousness=traits.conscientiousness,
            neuroticism=traits.neuroticism,
            openness=traits.openness,
            dominance=traits.dominance,
            empathy=traits.empathy,
            risk_taking=traits.risk_taking,
            emotional_stability=traits.emotional_stability,
            self_control=traits.self_control,
        )
