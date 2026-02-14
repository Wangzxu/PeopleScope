from core.agent import LLMFactory
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler

from repository.AggregationRepository import AggregationRepository
from repository.ChatRepository import ChatRepository
from repository.QuestionTraitRepository import QuestionRepository
from repository.ReflectionRepository import ReflectionRepository
from repository.SessionRepository import SessionRepository
from repository.UserRepository import UserRepository

from service.AggregationService import AggregationService
from service.ChatService import ChatService
from service.QuestionService import QuestionService
from service.ReflectionService import ReflectionService
from service.SessionService import SessionService
from service.UserService import UserService


class Container:
    """
    依赖注入容器，管理数据库连接、Repository 和 Service 的实例化与依赖装配。
    使用懒加载模式 (@property)，仅在需要时初始化组件。
    """

    def __init__(self):
        # 内部变量初始化为 None
        self._mysql = None
        self._mongo = None

        self._agg_repo = None
        self._chat_repo = None
        self._question_repo = None
        self._reflection_repo = None
        self._session_repo = None
        self._user_repo = None

        self._agg_service = None
        self._chat_service = None
        self._question_service = None
        self._reflection_service = None
        self._session_service = None
        self._user_service = None

        self._llm = None

    # --- Database Handlers ---

    @property
    def mysql(self):
        if self._mysql is None:
            self._mysql = MySQLHandler()
        return self._mysql

    @property
    def mongo(self):
        if self._mongo is None:
            self._mongo = MongoHandler()
        return self._mongo

    # --- Repositories ---

    @property
    def agg_repo(self):
        if self._agg_repo is None:
            self._agg_repo = AggregationRepository(self.mysql, self.mongo)
        return self._agg_repo

    @property
    def chat_repo(self):
        if self._chat_repo is None:
            self._chat_repo = ChatRepository(self.mysql, self.mongo)
        return self._chat_repo

    @property
    def question_repo(self):
        if self._question_repo is None:
            self._question_repo = QuestionRepository(self.mysql, self.mongo)
        return self._question_repo

    @property
    def reflection_repo(self):
        if self._reflection_repo is None:
            self._reflection_repo = ReflectionRepository(self.mysql, self.mongo)
        return self._reflection_repo

    @property
    def session_repo(self):
        if self._session_repo is None:
            self._session_repo = SessionRepository(self.mysql, self.mongo)
        return self._session_repo

    @property
    def user_repo(self):
        if self._user_repo is None:
            self._user_repo = UserRepository(self.mysql, self.mongo)
        return self._user_repo

    # --- Services ---

    @property
    def agg_service(self):
        if self._agg_service is None:
            self._agg_service = AggregationService(self.agg_repo, self.reflection_repo)
        return self._agg_service

    @property
    def question_service(self):
        if self._question_service is None:
            self._question_service = QuestionService(self.question_repo)
        return self._question_service

    @property
    def reflection_service(self):
        if self._reflection_service is None:
            self._reflection_service = ReflectionService(self.reflection_repo)
        return self._reflection_service

    @property
    def user_service(self):
        if self._user_service is None:
            self._user_service = UserService(
                self.user_repo, self.agg_repo, self.session_repo, self.chat_repo
            )
        return self._user_service

    @property
    def chat_service(self):
        if self._chat_service is None:
            self._chat_service = ChatService(self.chat_repo)
            # 处理依赖注入 (注意循环依赖的处理顺序)
            self._chat_service.set_user_service(self.user_service)
            # 触发 SessionService 初始化，SessionService 反过来会获取 chat_service (此时已不为 None)
            self._chat_service.set_session_service(self.session_service)
        return self._chat_service

    @property
    def session_service(self):
        if self._session_service is None:
            self._session_service = SessionService(self.session_repo, self.chat_repo)
            # 触发 ChatService 初始化，ChatService 反过来会获取 session_service (此时已不为 None)
            self._session_service.set_chat_service(self.chat_service)
        return self._session_service

    # --- Helper Methods ---

    def get_model(self):
        """
        获取 Model 工厂
        :return:
        """
        if self._llm is None:
            self._llm = LLMFactory()
        return self._llm

    def get_mysql_db(self):
        """
        获取 MySQL 数据库会话 (Generator)，用于 FastAPI 依赖注入。
        """
        db = self.mysql.get_session()
        try:
            yield db
        finally:
            db.close()
    
    @property
    def mysql_engine(self):
        """获取 MySQL 引擎实例 (兼容性)"""
        return self.mysql.get_engine()


# 实例化全局容器
db_container = Container()
