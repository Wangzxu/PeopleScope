from sqlalchemy.orm import declarative_base
from core.db_container import db_container

# 使用容器中的引擎
engine = db_container.mysql_engine

# 保持 Base 定义，供模型使用
Base = declarative_base()

def get_db():
    """
    (Deprecated) 建议直接使用 db_container.get_mysql_db
    保持此函数是为了兼容性。
    """
    return db_container.get_mysql_db()