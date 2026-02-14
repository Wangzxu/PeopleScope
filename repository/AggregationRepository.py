from sqlalchemy.orm import Session
from model.aggregation import AggregationModel
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class AggregationRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def create(self, entity: AggregationModel, db: Session = None):
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

    def update(self, entity: AggregationModel, db: Session = None):
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

    def get_by_id(self, entity_id: int, db: Session = None):
        session = db or self.mysql.get_session()
        try:
            entity = session.get(AggregationModel, entity_id)
            return entity
        finally:
            if db is None:
                session.close()

    def get_by_user(self, user: str, db: Session = None):
        session = db or self.mysql.get_session()
        try:
            return session.query(AggregationModel).filter(AggregationModel.user == user).first()
        finally:
            if db is None:
                session.close()
