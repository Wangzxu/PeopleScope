from sqlalchemy.orm import Session

from repository.ChatRepository import ChatRepository
from repository.UserRepository import UserRepository
from repository.AggregationRepository import AggregationRepository
from repository.SessionRepository import SessionRepository
from agent.UserTagGenerateAgent import generate_tag


class UserService:
    def __init__(self, 
                 user_repo: UserRepository, 
                 agg_repo: AggregationRepository, 
                 session_repo: SessionRepository, 
                 chat_repo: ChatRepository):
        self.user_repo = user_repo
        self.agg_repo = agg_repo
        self.session_repo = session_repo
        self.chat_repo = chat_repo

    def get_user(self, user: str, db: Session = None):
        return self.user_repo.get_user_by_name(user, db)

    def generate_tag(self, user: str, db: Session = None):
        aggregate = self.agg_repo.get_by_user(user, db)
        sessions = self.session_repo.get_session_by_user(user, db)
        conver = []
        title = []
        i = 0
        for session in sessions:
            chats = self.chat_repo.get_chats_by_session(session.id, db)
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
        user_entity = self.user_repo.get_user_by_name(user, db)
        user_entity.tags = tags
        self.user_repo.update_user(user_entity, db)
        return user_entity