# repositories/question_repo.py
from typing import List, cast

from sqlalchemy import func
from sqlalchemy.orm import Session
from model.question import QuestionTrait


class QuestionRepository:

    @staticmethod
    def create(db: Session, entity: QuestionTrait):
        db.add(entity)
        db.commit()
        db.refresh(entity)
        return entity

    @staticmethod
    def add_list(db: Session, data: List[QuestionTrait]):
        if not data:
            return 0

        db.add_all(data)
        db.commit()

        return len(data)

    @staticmethod
    def list(db: Session, number: int) -> List[QuestionTrait]:
        result = db.query(QuestionTrait).order_by(func.random()).limit(number).all()
        return cast(List[QuestionTrait], result)
