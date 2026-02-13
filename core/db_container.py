from datetime import datetime
from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler

class DBContainer:
    """
    数据库容器类，负责初始化和管理 MySQL 和 MongoDB 的连接。
    """

    def __init__(self):
        # 初始化 MySQL 和 MongoDB 处理器
        self.mysql_handler = MySQLHandler()
        self.mongo_handler = MongoHandler()

    def get_mysql(self):
        """
        获取 MySQL 会话实例。
        """
        return self.mysql_handler.get_session()

    def get_mongodb(self):
        """
        获取 MongoDB 数据库实例。
        """
        return self.mongo_handler.get_db()

    @property
    def mysql_engine(self):
        """获取 MySQL 引擎实例 (兼容性)"""
        return self.mysql_handler.get_engine()

    @property
    def mongo_db(self):
        """获取 MongoDB 数据库实例 (兼容性)"""
        return self.mongo_handler.get_db()

    def get_mysql_db(self):
        """
        获取 MySQL 数据库会话 (Generator)，用于 FastAPI 依赖注入。
        """
        db = self.get_mysql()
        try:
            yield db
        finally:
            db.close()

    def get_mongo_collection(self, collection_name: str):
        """获取 MongoDB 集合"""
        return self.mongo_handler.get_collection(collection_name)

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