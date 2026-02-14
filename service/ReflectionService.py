from sqlalchemy.orm import Session
from schema.relectionSchema import Reflection
from repository.ReflectionRepository import ReflectionRepository
from agent.ReflectionAgent import generate_reflection
from model.reflection import ReflectionModel


class ReflectionService:
    def __init__(self, reflection_repo: ReflectionRepository):
        self.reflection_repo = reflection_repo

    def get_reflection(self, dto: Reflection, db: Session = None):
        summary, traits = generate_reflection(dto)
        reflection = ReflectionModel.from_model(
            user=dto.user,
            question=dto.question,
            answer=dto.answer,
            question_id=dto.question_id,
            summary=summary,
            traits=traits
        )
        self.reflection_repo.create(reflection, db)
        return reflection