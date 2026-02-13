from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler


class Container:
    """
    数据库容器类，负责初始化和管理 MySQL 和 MongoDB 的连接。
    """
    def __init__(self):
        # 初始化 MySQL 和 MongoDB 处理器作为类属性
        self._mysql = None
        self._mongo = None

    def get_mysql_db(self):
        """
        获取 MySQL 数据库会话 (Generator)，用于 FastAPI 依赖注入。
        """
        if self._mysql is None:
            self._mysql = MySQLHandler()
        db = self._mysql.get_session()
        try:
            yield db
        finally:
            db.close()

    # container.mongo

    @property
    def get_mongo_db(self):
        """获取 MongoDB实例 (兼容性)"""
        if self._mongo is None:
            self._mongo = MongoHandler()
        return self._mongo.get_db()


# 实例化全局容器
db_container = Container()

