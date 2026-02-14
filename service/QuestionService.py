from sqlalchemy.orm import Session
from repository.QuestionTraitRepository import QuestionRepository
from schema.questionSchema import QuestionTraitCreate
from model.question import QuestionTrait
from agent.QuestionGenerateAgent import generate_questions


class QuestionService:
    def __init__(self, question_repo: QuestionRepository):
        self.question_repo = question_repo

    def create_question(self, dto: QuestionTraitCreate, db: Session = None):
        if not (1 <= dto.trait_score <= 10):
            raise ValueError("trait 必须在 1~10 之间")
        entity = QuestionTrait(
            question=dto.question,
            trait_score=dto.trait_score
        )

        return self.question_repo.create(entity, db)

    def generate_questions(self, number: int, db: Session = None):
        questions = generate_questions(number)
        return self.question_repo.add_list(questions, db)

    def get_questions(self, number: int, db: Session = None):
        questions = self.question_repo.list(number, db)
        result = []
        for question in questions:
            dto = QuestionTraitCreate(
                question_id=question.id,
                question=question.question,
                trait_score=question.trait_score
            )
            result.append(dto)
        return result