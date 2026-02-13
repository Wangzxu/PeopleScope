from pymongo import MongoClient
from pymongo.database import Database
from core.config import MONGO_URI, MONGO_DB_NAME

class MongoHandler:
    """
    MongoDB 数据库处理类，负责初始化客户端连接。
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
