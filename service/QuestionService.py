from sqlalchemy.orm import Session
from repository.QuestionTraitRepository import QuestionRepository
from schema.questionSchema import QuestionTraitCreate
from model.question import QuestionTrait
from agent.QuestionGenerateAgent import generate_questions


class QuestionService:

    @staticmethod
    def create_question(db: Session, dto: QuestionTraitCreate):
        if not (1 <= dto.trait_score <= 10):
            raise ValueError("trait 必须在 1~10 之间")
        entity = QuestionTrait(
            question=dto.question,
            trait_score=dto.trait_score
        )

        return QuestionRepository.create(db, entity)

    @staticmethod
    def generate_questions(db: Session, number: int):
        questions = generate_questions(number)
        return QuestionRepository.add_list(db, questions)

    @staticmethod
    def get_questions(db: Session, number: int):
        questions = QuestionRepository.list(db, number)
        result = []
        for question in questions:
            dto = QuestionTraitCreate(
                question_id=question.id,
                question=question.question,
                trait_score=question.trait_score
            )
            result.append(dto)
        return result

