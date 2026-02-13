from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, func
from model.reflection import ReflectionModel
from model.trait_vector import TraitVector
from core.db.database import Base


class AggregationModel(Base):
    """
    聚合分析模型，存储基于多次反思生成的综合性格报告。
    """
    __tablename__ = "aggregation"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")

    # 五大性格特质 (Big Five)
    extroversion = Column(Integer, nullable=False, comment="外向性")
    agreeableness = Column(Integer, nullable=False, comment="宜人性")
    conscientiousness = Column(Integer, nullable=False, comment="尽责性")
    neuroticism = Column(Integer, nullable=False, comment="神经质")
    openness = Column(Integer, nullable=False, comment="开放性")
    
    # 其他特质
    dominance = Column(Integer, nullable=False, comment="支配性")
    empathy = Column(Integer, nullable=False, comment="共情能力")
    risk_taking = Column(Integer, nullable=False, comment="冒险倾向")
    emotional_stability = Column(Integer, nullable=False, comment="情绪稳定性")
    self_control = Column(Integer, nullable=False, comment="自控力")

    summary = Column(Text, comment="综合评价/摘要")
    created_at = Column(TIMESTAMP, server_default=func.now(), comment="创建时间")

    @property
    def personality(self) -> TraitVector:
        """转换为 TraitVector 对象"""
        return TraitVector(
            extroversion=self.extroversion,
            agreeableness=self.agreeableness,
            conscientiousness=self.conscientiousness,
            neuroticism=self.neuroticism,
            openness=self.openness,
            dominance=self.dominance,
            empathy=self.empathy,
            risk_taking=self.risk_taking,
            emotional_stability=self.emotional_stability,
            self_control=self.self_control,
        )

    @staticmethod
    def from_reflection(
            reflection: ReflectionModel,
            traits: TraitVector,
    ) -> 'AggregationModel':
        """
        工厂方法：从反思记录和特征向量创建聚合模型
        """
        return AggregationModel(
            user=reflection.user,
            summary=reflection.summary,

            extroversion=traits.extroversion,
            agreeableness=traits.agreeableness,
            conscientiousness=traits.conscientiousness,
            neuroticism=traits.neuroticism,
            openness=traits.openness,
            dominance=traits.dominance,
            empathy=traits.empathy,
            risk_taking=traits.risk_taking,
            emotional_stability=traits.emotional_stability,
            self_control=traits.self_control,
        )
