from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from core.db.database import Base


class SessionModel(Base):
    """
    会话模型，存储聊天会话的基本信息。
    """
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")
    title = Column(String(255), nullable=False, comment="会话标题")
    content = Column(Text, nullable=False, comment="会话上下文/摘要")  # 或 JSONB
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
