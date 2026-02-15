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

    def save_chat_mongo(self, chat: ChatModel, user: str):
        self.mongo.save_chat(
            session_id=chat.session_id,
            message_type=chat.type,
            content=chat.content,
            user=user
        )

    def get_related_chats(self, user: str, query_text: str, limit: int = 3):
        try:
            return self.mongo.get_related_chats(user, query_text, limit)
        except Exception:
            # 如果文本搜索失败（例如索引未建立），返回空列表或进行错误处理
            return []

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
