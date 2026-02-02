from fastapi import Depends
from core.database import get_db
from schema.relectionSchema import Reflection
from repository.ReflectionRepository import ReflectionRepository
from agent.ReflectionAgent import generate_reflection
from model.reflection import ReflectionModel


class ReflectionService:
    @staticmethod
    def get_reflection(db: Depends(get_db), dto: Reflection):
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
