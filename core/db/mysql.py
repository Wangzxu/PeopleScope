from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from core.config import DATABASE_URL

class MySQLHandler:
    """
    MySQL 数据库处理类，负责初始化引擎和会话工厂。
    """
    def __init__(self):
        # 初始化 MySQL 引擎
        self.engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,  # 自动重连
            pool_size=10,        # 连接池大小
            max_overflow=20,     # 最大溢出连接数
            echo=False           # 是否打印 SQL 语句
        )
        # 创建会话工厂
        self.session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

    def get_session(self) -> Session:
        """获取一个新的数据库会话"""
        return self.session_factory()

    def get_engine(self):
        """获取数据库引擎"""
        return self.engine
