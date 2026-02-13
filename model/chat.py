from sqlalchemy import Column, Integer, Text, SmallInteger, DateTime, func
from core.db.mysql import Base


class ChatModel(Base):
    """
    聊天记录模型，存储会话中的单条消息。
    """
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    session_id = Column(Integer, nullable=False, index=True, comment="所属会话ID")

    msg_index = Column(Integer, nullable=False, comment="消息序号")

    type = Column(SmallInteger, nullable=False, comment="消息类型(0:用户, 1:AI)")
    content = Column(Text, nullable=False, comment="消息内容")
    created_at = Column(DateTime, server_default=func.now(), comment="创建时间")
