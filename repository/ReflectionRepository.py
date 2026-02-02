from typing import List
from sqlalchemy.orm import Session
from model.reflection import ReflectionModel


class ReflectionRepository:
    @staticmethod
    def list_by_user(db: Session, user: str) -> List[ReflectionModel]:
        return db.query(ReflectionModel).filter(ReflectionModel.user == user).all()

    @staticmethod
    def create(db: Session, entity: ReflectionModel):
        existing = db.query(ReflectionModel).filter(
            ReflectionModel.user == entity.user,
            ReflectionModel.question_id == entity.question_id
        ).first()

        if existing:
            existing.answer = entity.answer
            existing.traits = entity.traits
            db.commit()
            db.refresh(existing)
            return existing
        else:
            db.add(entity)
            db.commit()
            db.refresh(entity)
            return entity
