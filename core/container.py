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
    """

    def __init__(self):
        # 1. 初始化数据库处理器
        self.mysql = MySQLHandler()
        self.mongo = MongoHandler()

        # 2. 初始化 Repositories (注入 DB Handlers)
        self.agg_repo = AggregationRepository(self.mysql, self.mongo)
        self.chat_repo = ChatRepository(self.mysql, self.mongo)
        self.question_repo = QuestionRepository(self.mysql, self.mongo)
        self.reflection_repo = ReflectionRepository(self.mysql, self.mongo)
        self.session_repo = SessionRepository(self.mysql, self.mongo)
        self.user_repo = UserRepository(self.mysql, self.mongo)

        # 3. 初始化 Services (注入 Repositories)
        self.user_service = UserService(
            self.user_repo, self.agg_repo, self.session_repo, self.chat_repo
        )
        self.agg_service = AggregationService(self.agg_repo, self.reflection_repo)
        self.question_service = QuestionService(self.question_repo)
        self.reflection_service = ReflectionService(self.reflection_repo)

        # 4. 处理循环依赖 (ChatService <-> SessionService)
        self.chat_service = ChatService(self.chat_repo)
        self.session_service = SessionService(self.session_repo, self.chat_repo)

        # 注入循环依赖
        self.chat_service.set_session_service(self.session_service)
        self.chat_service.set_user_service(self.user_service)
        
        self.session_service.set_chat_service(self.chat_service)

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