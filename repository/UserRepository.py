from sqlalchemy.orm import Session
from model.user import UserModel
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class UserRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def get_user_by_name(self, user: str) -> UserModel:
        session = self.mysql.get_session()
        try:
            return session.query(UserModel).filter(UserModel.user == user).first()
        finally:
            session.close()

    def update_user(self, user: UserModel):
        session = self.mysql.get_session()
        try:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user
        except:
            session.rollback()
            raise
        finally:
            session.close()