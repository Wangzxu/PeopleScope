from sqlalchemy import Column, Integer, Text
from core.db.mysql import Base


class QuestionTrait(Base):
    """
    问题模型，存储用于性格评估的问题库。
    """
    __tablename__ = "question_trait"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    question = Column(Text, nullable=False, comment="问题文本")
    trait_score = Column(Integer, comment="预设评分(1~10)")  # 1~10，应用逻辑控制
