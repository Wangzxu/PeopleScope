from model.chat import ChatModel
from core.db.mysql import MySQLHandler
from core.db.chroma import ChromaHandler


class ChatRepository:
    def __init__(self, mysql: MySQLHandler, chroma: ChromaHandler):
        self.mysql = mysql
        self.chroma = chroma

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

    def save_chat_chroma(self, chat: ChatModel, user: str):
        # 使用 ChromaDB 存储
        self.chroma.add_chat(
            user=user,
            content=chat.content,
            metadata={
                "session_id": chat.session_id,
                "type": chat.type,
                "user": user
            }
        )
        
    def save_fact_chroma(self, fact_text: str, user: str, session_id: int):
        """保存提取的事实到 ChromaDB"""
        self.chroma.add_chat(
            user=user,
            content=fact_text,
            metadata={
                "session_id": session_id,
                "type": 2, # Use type 2 for facts
                "user": user
            }
        )

    def check_fact_exists(self, user: str, fact_text: str, threshold: float = 0.15) -> bool:
        """检查是否存在相似事实"""
        return self.chroma.check_fact_exists(user, fact_text, threshold)

    def get_related_facts(self, user: str, query_text: str, limit: int = 3):
        try:
            return self.chroma.query_similar_facts(user, query_text, n_results=limit)
        except Exception:
            return []

    def get_related_chats(self, user: str, query_text: str, limit: int = 3):
        try:
            return self.chroma.query_similar_chats(user, query_text, n_results=limit)
        except Exception:
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
