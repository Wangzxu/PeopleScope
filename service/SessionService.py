from repository.SessionRepository import SessionRepository
from repository.ChatRepository import ChatRepository


class SessionService:
    def __init__(self, session_repo: SessionRepository, chat_repo: ChatRepository, title_agent):
        self.session_repo = session_repo
        self.chat_repo = chat_repo
        self.title_agent = title_agent
        self.chat_service = None

    def set_chat_service(self, chat_service):
        self.chat_service = chat_service

    def get_sessions(self, user: str):
        return self.session_repo.get_session_by_user(user)

    def get_session(self, session_id: int):
        return self.session_repo.get_session_by_id(session_id)

    def create_session(self, user: str, message: str):
        # 1. 生成标题
        title = self.title_agent.get_title(message)
        
        # 2. 创建Session
        content = message
        session = self.session_repo.create_session(user, title, content)
        
        # 3. 生成回复并保存对话
        if self.chat_service:
            # 0 代表用户发言
            self.chat_service.save_chat(session.id, 0, message)
            
            # 生成并保存AI回复 (1 代表AI发言)
            ans = self.chat_service.generate_chat(user, session.id, message)
            self.chat_service.save_chat(session.id, 1, ans)
        
        return session

    def rename_session(self, session_id: int, title: str):
        return self.session_repo.update_session_title(session_id, title)

    def delete_session(self, session_id: int):
        # 先删除聊天记录
        self.chat_repo.delete_chats_by_session(session_id)
        # 再删除会话
        return self.session_repo.delete_session(session_id)
