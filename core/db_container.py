from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pymongo import MongoClient
from core.config import DATABASE_URL, MONGO_URI, MONGO_DB_NAME
from datetime import datetime

class DBContainer:
    """
    数据库容器类，负责初始化和管理 MySQL 和 MongoDB 的连接。
    """
    def __init__(self):
        # 初始化 MySQL 连接池
        self._mysql_engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,   # 自动重连
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        # 创建 MySQL 会话工厂
        self._mysql_session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self._mysql_engine
        )

        # 初始化 MongoDB 客户端
        self._mongo_client = MongoClient(MONGO_URI)
        self._mongo_db = self._mongo_client[MONGO_DB_NAME]

    @property
    def mysql_engine(self):
        """获取 MySQL 引擎实例"""
        return self._mysql_engine

    @property
    def mongo_db(self):
        """获取 MongoDB 数据库实例"""
        return self._mongo_db

    def get_mysql_db(self):
        """
        获取 MySQL 数据库会话 (Generator)，用于 FastAPI 依赖注入。
        """
        db = self._mysql_session_factory()
        try:
            yield db
        finally:
            db.close()

    def get_mongo_collection(self, collection_name: str):
        """获取 MongoDB 集合"""
        return self._mongo_db[collection_name]

    # MongoDB 数据存储辅助函数

    def save_user_tags(self, user: str, tags: dict):
        """
        保存或更新用户标签。
        :param user: 用户名
        :param tags: 标签字典
        """
        collection = self.get_mongo_collection("user_tags")
        collection.update_one(
            {"user": user},
            {"$set": {"tags": tags, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    def save_chat(self, session_id: int, message_type: int, content: str, user: str = None):
        """
        保存聊天记录。
        :param session_id: 会话ID
        :param message_type: 0 (用户) 或 1 (AI)
        :param content: 消息内容
        :param user: 可选关联用户名
        """
        collection = self.get_mongo_collection("chats")
        chat_doc = {
            "session_id": session_id,
            "type": message_type,
            "content": content,
            "created_at": datetime.utcnow()
        }
        if user:
            chat_doc["user"] = user
        collection.insert_one(chat_doc)

    def save_aggregation(self, user: str, aggregation_data: dict):
        """
        保存用户聚合分析结果。
        :param user: 用户名
        :param aggregation_data: 聚合数据字典
        """
        collection = self.get_mongo_collection("aggregations")
        update_data = aggregation_data.copy()
        update_data["updated_at"] = datetime.utcnow()
        
        collection.update_one(
            {"user": user},
            {"$set": update_data},
            upsert=True
        )

# 实例化全局容器
db_container = DBContainer()
