from sqlalchemy import Column, Integer, String, JSON, TIMESTAMP, func
from core.db.database import Base


class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user = Column(String(64), nullable=False)
    age = Column(Integer)
    profession = Column(String(64))
    work = Column(String(128))
    tags = Column(JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
