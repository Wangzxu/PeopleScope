from typing import List
from sqlalchemy.orm import Session
from model.reflection import ReflectionModel
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class ReflectionRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def list_by_user(self, user: str) -> List[ReflectionModel]:
        session = self.mysql.get_session()
        try:
            return session.query(ReflectionModel).filter(ReflectionModel.user == user).all()
        finally:
            session.close()

    def create(self, entity: ReflectionModel):
        session = self.mysql.get_session()
        try:
            existing = session.query(ReflectionModel).filter(
                ReflectionModel.user == entity.user,
                ReflectionModel.question_id == entity.question_id
            ).first()

            if existing:
                existing.answer = entity.answer
                existing.traits = entity.traits
                session.commit()
                session.refresh(existing)
                return existing
            else:
                session.add(entity)
                session.commit()
                session.refresh(entity)
                return entity
        except:
            session.rollback()
            raise
        finally:
            session.close()