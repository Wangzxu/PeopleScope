from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, JSON, func
from core.db.database import Base
from model.trait_vector import TraitVector


class ReflectionModel(Base):
    """
    反思模型，存储用户对问题的回答及生成的性格特征分析。
    """
    __tablename__ = "reflection"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")
    question = Column(Text, nullable=False, comment="问题内容")
    answer = Column(Text, nullable=False, comment="用户回答")
    summary = Column(Text, nullable=True, comment="回答摘要")
    question_id = Column(Integer, nullable=False, comment="关联的问题ID")
    traits = Column(JSON, nullable=False, comment="分析出的性格特征(JSON)")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")

    @staticmethod
    def from_model(user: str, question: str, question_id: int, answer: str, summary: str, traits: TraitVector):
        """
        工厂方法：从业务数据创建模型实例
        """
        return ReflectionModel(
            user=user,
            question=question,
            answer=answer,
            summary=summary,
            question_id=question_id,
            traits=traits.dict() if hasattr(traits, 'dict') else traits.__dict__
        )
