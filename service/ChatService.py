from core.logger import get_logger
from model.chat import ChatModel
from repository.ChatRepository import ChatRepository

logger = get_logger(__name__)


# Removed direct imports of Service classes to avoid circular imports at module level
# Will inject instances


class ChatService:
    def __init__(self, chat_repo: ChatRepository, chat_agent):
        self.chat_repo = chat_repo
        self.chat_agent = chat_agent
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

        # 获取最相关的3条事实记忆
        related_facts = self.chat_repo.get_related_facts(user, message, limit=3)

        # 把变量直接放进字符串大括号里
        logger.info(f"最相关的三个记忆片段：{related_facts}")

        answer, facts = self.chat_agent.generate_answer(title, user, entity.tags, message, session_id, related_facts)
        
        # 处理提取的事实
        if facts:
            logger.info(f"提取到新事实：{facts}")
            for fact in facts:
                # check similarity > 95% (distance < 0.15)
                if not self.chat_repo.check_fact_exists(user, fact, threshold=0.15):
                    logger.info(f"存储新事实: {fact}")
                    self.chat_repo.save_fact_chroma(fact, user, session_id)
                else:
                    logger.info(f"事实已存在，跳过存储: {fact}")
        else:
            logger.info(f"未提取到事实")

        return answer

    def save_chat(self, session_id: int, type: int, content: str):
        chats = self.chat_repo.get_chats_by_session(session_id)
        if len(chats) > 0:
            msg_index = chats[-1].msg_index + 1
        else:
            msg_index = 0
        chat = ChatModel(session_id=session_id, type=type, content=content, msg_index=msg_index)

        # 保存到 MySQL
        saved_chat = self.chat_repo.save_chat(chat)

        return saved_chat
