from sqlalchemy.orm import Session

from model.chat import ChatModel
from repository.ChatRepository import ChatRepository
from service.SessionService import SessionService
from agent.ChatAgent import generate_answer
from service.UserService import UserService


class ChatService:
    @staticmethod
    def get_chats(db: Session, session_id: int):
        return ChatRepository.get_chats_by_session(db, session_id)

    @staticmethod
    def generate_chat(db: Session, user: str, session_id: int, message: str):
        session = SessionService.get_session(db, session_id)
        title = session.title
        entity = UserService.get_user(db, user)
        return generate_answer(title, user, entity.tags, message, session_id)

    @staticmethod
    def save_chat(db: Session, session_id: int, type: int, content: str):
        chats = ChatRepository.get_chats_by_session(db, session_id)
        if len(chats) > 0:
            msg_index = chats[-1].msg_index + 1
        else:
            msg_index = 0
        chat = ChatModel(session_id=session_id, type=type, content=content, msg_index=msg_index)
        return ChatRepository.save_chat(db, chat)
