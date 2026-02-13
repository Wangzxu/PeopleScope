from sqlalchemy import Column, Integer, Text
from core.db.database import Base


class QuestionTrait(Base):
    __tablename__ = "question_trait"

    id = Column(Integer, primary_key=True, autoincrement=True)
    question = Column(Text, nullable=False)
    trait_score = Column(Integer)  # 1~10，应用逻辑控制
