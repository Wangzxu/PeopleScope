from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func
from core.db.database import Base


class UserModel(Base):
    """
    用户模型，存储用户基本信息及画像标签。
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")
    age = Column(Integer, comment="年龄")
    profession = Column(String(64), comment="职业")
    work = Column(String(128), comment="工作内容/职位")
    tags = Column(JSON, comment="用户标签(JSON)")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment="更新时间")
