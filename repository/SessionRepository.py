from sqlalchemy.orm import Session
from model.session import SessionModel
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class SessionRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def get_session_by_user(self, user: str):
        session = self.mysql.get_session()
        try:
            return session.query(SessionModel).filter(SessionModel.user == user).all()
        finally:
            session.close()

    def get_session_by_id(self, session_id: int):
        session = self.mysql.get_session()
        try:
            return session.query(SessionModel).filter(SessionModel.id == session_id).first()
        finally:
            session.close()

    def create_session(self, user: str, title: str, content: str):
        session = self.mysql.get_session()
        try:
            session_model = SessionModel(user=user, title=title, content=content)
            session.add(session_model)
            session.commit()
            session.refresh(session_model)
            return session_model
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def update_session_title(self, session_id: int, title: str):
        session = self.mysql.get_session()
        try:
            session_model = session.query(SessionModel).filter(SessionModel.id == session_id).first()
            if session_model:
                session_model.title = title
                session.commit()
                session.refresh(session_model)
            return session_model
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_session(self, session_id: int):
        session = self.mysql.get_session()
        try:
            session_model = session.query(SessionModel).filter(SessionModel.id == session_id).first()
            if session_model:
                session.delete(session_model)
                session.commit()
                return True
            return False
        except:
            session.rollback()
            raise
        finally:
            session.close()