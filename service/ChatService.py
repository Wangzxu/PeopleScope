from model.chat import ChatModel
from repository.ChatRepository import ChatRepository
from agent.ChatAgent import generate_answer
# Removed direct imports of Service classes to avoid circular imports at module level
# Will inject instances


class ChatService:
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
        self.session_service = None
        self.user_service = None

    def set_session_service(self, session_service):
        self.session_service = session_service

    def set_user_service(self, user_service):
        self.user_service = user_service

    def get_chats(self, session_id: int):
        return self.chat_repo.get_chats_by_session(session_id)

    def generate_chat(self, user: str, session_id: int, message: str):
        # Dependencies: SessionService, UserService
        session = self.session_service.get_session(session_id)
        title = session.title
        entity = self.user_service.get_user(user)
        return generate_answer(title, user, entity.tags, message, session_id)

    def save_chat(self, session_id: int, type: int, content: str):
        chats = self.chat_repo.get_chats_by_session(session_id)
        if len(chats) > 0:
            msg_index = chats[-1].msg_index + 1
        else:
            msg_index = 0
        chat = ChatModel(session_id=session_id, type=type, content=content, msg_index=msg_index)
        return self.chat_repo.save_chat(chat)
