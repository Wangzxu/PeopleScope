from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, func
from sqlalchemy.ext.declarative import declarative_base
from model.trait_vector import TraitVector  # 假设这是你自己的类

Base = declarative_base()


@dataclass
class ReflectionModel(Base):
    __tablename__ = "reflection"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user: str = Column(String(64), nullable=False)
    question: str = Column(Text, nullable=False)
    answer: str = Column(Text, nullable=False)
    summary: str = Column(Text, nullable=True)
    question_id: int = Column(Integer, nullable=False)

    # traits 可以存成 JSON
    traits: dict = Column(JSON, nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())

    @staticmethod
    def from_model(user: str, question: str, question_id: int, answer: str, summary: str, traits: TraitVector):
        return ReflectionModel(
            user=user,
            question=question,
            answer=answer,
            summary=summary,
            question_id=question_id,
            traits=traits.__dict__
        )
