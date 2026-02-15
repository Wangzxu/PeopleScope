from datetime import datetime
from pymongo import MongoClient
from pymongo.database import Database
from core.config import MONGO_URI, MONGO_DB_NAME


class MongoHandler:
    """
    MongoDB 数据库处理类，负责初始化客户端连接及具体数据操作。
    """

    def __init__(self):
        # 初始化 MongoDB 客户端
        self.client = MongoClient(MONGO_URI)
        self.db = self.client[MONGO_DB_NAME]

    def get_db(self) -> Database:
        """获取 MongoDB 数据库实例"""
        return self.db

    def get_collection(self, collection_name: str):
        """获取指定的集合"""
        return self.db[collection_name]

    # MongoDB 数据存储辅助函数

    def save_user_tags(self, user: str, tags: dict):
        """
        保存或更新用户标签。
        :param user: 用户名
        :param tags: 标签字典
        """
        collection = self.get_collection("user_tags")
        collection.update_one(
            {"user": user},
            {"$set": {"tags": tags, "updated_at": datetime.utcnow()}},
            upsert=True
        )

    def get_related_chats(self, user: str, query_text: str, limit: int = 3):
        """
        获取与查询文本最相关的聊天记录。
        :param user: 用户名
        :param query_text: 查询文本
        :param limit: 返回数量限制
        :return: 相关聊天记录内容列表
        """
        collection = self.get_collection("chat")
        
        # 确保存在全文索引 (如果不存在则创建)
        collection.create_index([("content", "text")])
        
        cursor = collection.find(
            {"$text": {"$search": query_text}, "user": user, "type": 0},
            {"score": {"$meta": "textScore"}, "content": 1, "_id": 0}
        ).sort([("score", {"$meta": "textScore"})]).limit(limit)
        
        return [doc["content"] for doc in cursor]

    def save_chat(self, session_id: int, message_type: int, content: str, user: str = None):
        """
        保存聊天记录。
        :param session_id: 会话ID
        :param message_type: 0 (用户) 或 1 (AI)
        :param content: 消息内容
        :param user: 可选关联用户名
        """
        collection = self.get_collection("chat")
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
        collection = self.get_collection("aggregations")
        update_data = aggregation_data.copy()
        update_data["updated_at"] = datetime.utcnow()

        collection.update_one(
            {"user": user},
            {"$set": update_data},
            upsert=True
        )
