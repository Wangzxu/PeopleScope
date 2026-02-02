from sqlalchemy import Column, Integer, Text, SmallInteger, DateTime, func
from core.database import Base


class ChatModel(Base):
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, nullable=False, index=True)

    msg_index = Column(Integer, nullable=False)

    type = Column(SmallInteger, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
