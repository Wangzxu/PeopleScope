from sqlalchemy.orm import Session

from repository.ChatRepository import ChatRepository
from repository.UserRepository import UserRepository
from repository.AggregationRepository import AggregationRepository
from repository.SessionRepository import SessionRepository
from agent.UserTagGenerateAgent import generate_tag


class UserService:
    @staticmethod
    def get_user(db: Session, user: str):
        return UserRepository.get_user_by_name(db, user)

    @staticmethod
    def generate_tag(db: Session, user: str):
        aggregate = AggregationRepository.get_by_user(db, user)
        sessions = SessionRepository.get_session_by_user(db, user)
        conver = []
        title = []
        i = 0
        for session in sessions:
            chats = ChatRepository.get_chats_by_session(db, session.id)
            title.append(session.title)
            for chat in chats:
                if chat.type == 1:
                    conver.append(chat)
                    i += 1
                if i >= 10:
                    break

        style_tags, topic_tags = generate_tag(conver, aggregate.summary, title)
        tags = {
                "style": style_tags,
                "topic": topic_tags
            }
        user = UserRepository.get_user_by_name(db, user)
        user.tags = tags
        UserRepository.update_user(db, user)
        return user
