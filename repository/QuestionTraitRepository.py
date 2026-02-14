# repositories/question_repo.py
from typing import List, cast

from sqlalchemy import func
from sqlalchemy.orm import Session
from model.question import QuestionTrait
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class QuestionRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def create(self, entity: QuestionTrait, db: Session = None):
        session = db or self.mysql.get_session()
        try:
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except:
            session.rollback()
            raise
        finally:
            if db is None:
                session.close()

    def add_list(self, data: List[QuestionTrait], db: Session = None):
        if not data:
            return 0
        session = db or self.mysql.get_session()
        try:
            session.add_all(data)
            session.commit()
            return len(data)
        except:
            session.rollback()
            raise
        finally:
            if db is None:
                session.close()

    def list(self, number: int, db: Session = None) -> List[QuestionTrait]:
        session = db or self.mysql.get_session()
        try:
            result = session.query(QuestionTrait).order_by(func.random()).limit(number).all()
            return cast(List[QuestionTrait], result)
        finally:
            if db is None:
                session.close()