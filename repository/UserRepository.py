from sqlalchemy.orm import Session
from model.user import UserModel
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class UserRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def get_user_by_name(self, user: str, db: Session = None) -> UserModel:
        session = db or self.mysql.get_session()
        try:
            return session.query(UserModel).filter(UserModel.user == user).first()
        finally:
            if db is None:
                session.close()

    def update_user(self, user: UserModel, db: Session = None):
        session = db or self.mysql.get_session()
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except:
            session.rollback()
            raise
        finally:
            if db is None:
                session.close()