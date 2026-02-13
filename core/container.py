from core.db.mysql import MySQLHandler
from core.db.mongo import MongoHandler

class Container:
    """
    数据库容器类，负责初始化和管理 MySQL 和 MongoDB 的连接。
    """

    def __init__(self):
        # 初始化 MySQL 和 MongoDB 处理器作为类属性
        self.mysql = MySQLHandler()
        self.mongo = MongoHandler()

    def get_mysql_db(self):
        """
        获取 MySQL 数据库会话 (Generator)，用于 FastAPI 依赖注入。
        """
        db = self.mysql.get_session()
        try:
            yield db
        finally:
            db.close()
    
    # 兼容性属性/方法，如果需要直接访问 handler 可以直接使用 container.mysql 或
    # container.mongo
    
    @property
    def mysql_engine(self):
        """获取 MySQL 引擎实例 (兼容性)"""
        return self.mysql.get_engine()


# 实例化全局容器
db_container = Container()
