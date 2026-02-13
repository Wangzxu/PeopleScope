from pydantic import BaseModel, Field


class TraitVector(BaseModel):
    """
    性格特征向量模型，包含五大性格特质及其他关键心理维度。
    所有特质评分范围通常为 1-10。
    """
    extroversion: int = Field(default=5, description="外向性")
    agreeableness: int = Field(default=5, description="宜人性")
    conscientiousness: int = Field(default=5, description="尽责性")
    neuroticism: int = Field(default=5, description="神经质")
    openness: int = Field(default=5, description="开放性")
    dominance: int = Field(default=5, description="支配性")
    empathy: int = Field(default=5, description="共情能力")
    risk_taking: int = Field(default=5, description="冒险倾向")
    emotional_stability: int = Field(default=5, description="情绪稳定性")
    self_control: int = Field(default=5, description="自控力")

