from sqlalchemy import Column, Integer, String, Float, Text, Boolean, TIMESTAMP, Index
from sqlalchemy.sql import func
from core.db.mysql import Base


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="自增主键")
    source_user = Column(String(64), nullable=False, index=True, comment="发起搜索的用户ID (当前用户)")
    target_user = Column(String(64), nullable=False, comment="被匹配到的候选人ID")
    
    # 匹配质量指标
    score = Column(Float, default=0.0, index=True, comment="综合匹配得分 (0-100)")
    match_reason = Column(Text, comment="AI生成的推荐理由快照")
    
    # 状态控制
    is_viewed = Column(Boolean, default=False, comment="用户是否已查看该推荐")
    updated_at = Column(TIMESTAMP, server_default=func.current_timestamp(), onupdate=func.current_timestamp(), comment="记录最后更新时间")
