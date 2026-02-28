from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MatchResultSchema(BaseModel):
    id: Optional[int] = Field(None, description="主键ID")
    source_user: str = Field(..., description="发起搜索的用户ID (当前用户)")
    target_user: str = Field(..., description="被匹配到的候选人ID")
    score: Optional[float] = Field(0.0, description="综合匹配得分 (0-100)")
    match_reason: Optional[str] = Field(None, description="AI生成的推荐理由快照")
    is_viewed: Optional[bool] = Field(False, description="用户是否已查看该推荐")
    updated_at: Optional[datetime] = Field(None, description="匹配生成时间")
    
    class Config:
        from_attributes = True

class RecommendationScore(BaseModel):
    score: float = Field(..., description="综合匹配得分 (0-100)")
    match_reason: str = Field(..., description="AI生成的推荐理由快照，解释为什么匹配以及匹配的程度")
