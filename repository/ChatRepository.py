from sqlalchemy.orm import Session
from model.chat import ChatModel
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class ChatRepository:
    def __init__(self, mysql: MySQLHandler, mongo: MongoHandler):
        self.mysql = mysql
        self.mongo = mongo

    def get_chats_by_session(self, session_id):
        session = self.mysql.get_session()
        try:
            return (session.query(ChatModel)
                    .filter(ChatModel.session_id == session_id)
                    .order_by(ChatModel.msg_index)
                    .all())
        finally:
            session.close()

    def save_chat(self, chat: ChatModel):
        session = self.mysql.get_session()
        try:
            session.add(chat)
            session.commit()
            session.refresh(chat)
            return chat
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def delete_chats_by_session(self, session_id: int):
        session = self.mysql.get_session()
        try:
            session.query(ChatModel).filter(ChatModel.session_id == session_id).delete()
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
