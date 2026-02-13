from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from core.db.database import Base


class SessionModel(Base):
    __tablename__ = "session"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(64), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)  # 或 JSONB
    created_at = Column(DateTime(timezone=True), server_default=func.now())
