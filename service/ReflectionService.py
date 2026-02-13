from sqlalchemy.orm import Session
from schema.relectionSchema import Reflection
from repository.ReflectionRepository import ReflectionRepository
from agent.ReflectionAgent import generate_reflection
from model.reflection import ReflectionModel


class ReflectionService:
    @staticmethod
    def get_reflection(db: Session, dto: Reflection):
        summary, traits = generate_reflection(dto)
        reflection = ReflectionModel.from_model(
            user=dto.user,
            question=dto.question,
            answer=dto.answer,
            question_id=dto.question_id,
            summary=summary,
            traits=traits
        )
        ReflectionRepository.create(db, reflection)
        return reflection
