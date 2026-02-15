from schema.relectionSchema import Reflection
from repository.ReflectionRepository import ReflectionRepository
from model.reflection import ReflectionModel


class ReflectionService:
    def __init__(self, reflection_repo: ReflectionRepository, reflection_agent):
        self.reflection_repo = reflection_repo
        self.reflection_agent = reflection_agent

    def get_reflection(self, dto: Reflection):
        summary, traits = self.reflection_agent.generate_reflection(dto)
        reflection = ReflectionModel.from_model(
            user=dto.user,
            question=dto.question,
            answer=dto.answer,
            question_id=dto.question_id,
            summary=summary,
            traits=traits
        )
        self.reflection_repo.create(reflection)
        return reflection

