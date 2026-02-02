from sqlalchemy.orm import Session
from repository.SessionRepository import SessionRepository
from repository.ChatRepository import ChatRepository
from agent.TitleGenerateAgent import get_title


class SessionService:
    @staticmethod
    def get_sessions(db: Session, user: str):
        return SessionRepository.get_session_by_user(db, user)

    @staticmethod
    def get_session(db: Session, session_id: int):
        return SessionRepository.get_session_by_id(db, session_id)

    @staticmethod
    def create_session(db: Session, user: str, message: str):
        # 1. 生成标题
        title = get_title(message)
        
        # 2. 创建Session
        content = message
        session = SessionRepository.create_session(db, user, title, content)
        
        # 3. 生成回复并保存对话
        # 使用局部引用避免循环依赖
        from service.ChatService import ChatService
        
        # 0 代表用户发言
        ChatService.save_chat(db, session.id, 0, message)
        
        # 生成并保存AI回复 (1 代表AI发言)
        ans = ChatService.generate_chat(db, user, session.id, message)
        ChatService.save_chat(db, session.id, 1, ans)
        
        return session

    @staticmethod
    def rename_session(db: Session, session_id: int, title: str):
        return SessionRepository.update_session_title(db, session_id, title)

    @staticmethod
    def delete_session(db: Session, session_id: int):
        # 先删除聊天记录
        ChatRepository.delete_chats_by_session(db, session_id)
        # 再删除会话
        return SessionRepository.delete_session(db, session_id)


