from sqlalchemy.orm import Session
from model.chat import ChatModel


class ChatRepository:
    @staticmethod
    def get_chats_by_session(db: Session, session_id):
        return (db.query(ChatModel)
                .filter(ChatModel.session_id == session_id)
                .order_by(ChatModel.msg_index)
                .all())

    @staticmethod
    def save_chat(db: Session, chat: ChatModel):
        db.add(chat)
        db.commit()
        db.refresh(chat)
        return chat

    @staticmethod
    def delete_chats_by_session(db: Session, session_id: int):
        db.query(ChatModel).filter(ChatModel.session_id == session_id).delete()
        db.commit()