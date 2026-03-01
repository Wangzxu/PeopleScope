from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from model.basicHardware import BasicHardware
from model.matchResult import MatchResult
from core.db.mysql import MySQLHandler
from schema.hardwareSchema import FriendHardwareSchema
from typing import List


class MatchResultRepository:
    def __init__(self, mysql: MySQLHandler):
        self.mysql = mysql

    def check_needs_hard_filter(self, source_user: str) -> bool:
        session = self.mysql.get_session()
        from model.basicHardware import FriendHardware
        try:
            friend_hw = session.query(FriendHardware).filter(FriendHardware.user == source_user).first()
            if not friend_hw or not friend_hw.updated_at:
                return True

            latest_match = session.query(MatchResult).filter(MatchResult.source_user == source_user).order_by(MatchResult.updated_at.desc()).first()
            if not latest_match or not latest_match.updated_at:
                return True
            
            # 宽限几秒或直接判断
            if friend_hw.updated_at > latest_match.updated_at:
                return True
                
            return False
        finally:
            session.close()

    def get_existing_matches(self, source_user: str) -> List[MatchResult]:
        session = self.mysql.get_session()
        try:
            return session.query(MatchResult).filter(MatchResult.source_user == source_user).all()
        finally:
            session.close()

    def get_matches_with_details(self, source_user: str) -> List[dict]:
        """获取匹配结果，并带上目标用户的硬件信息，按分数倒序排列。"""
        session = self.mysql.get_session()
        try:
            results = session.query(MatchResult, BasicHardware)\
                .join(BasicHardware, MatchResult.target_user == BasicHardware.user)\
                .filter(MatchResult.source_user == source_user)\
                .order_by(MatchResult.score.desc())\
                .all()
                
            return [
                {
                    "match": match,
                    "hardware": hardware
                }
                for match, hardware in results
            ]
        finally:
            session.close()

    def get_candidates(self, friend_req: FriendHardwareSchema) -> List[BasicHardware]:
        session = self.mysql.get_session()
        try:
            # 基础过滤：排除当前用户
            query = session.query(BasicHardware).filter(BasicHardware.user != friend_req.user)
            
            # 以下为可选过滤条件，根据 friend_hardware_data 进行筛选
            # 注意: 为了保证能匹配到人，这里仅做一些基本过滤，复杂的依靠 LLM 打分
            
            if friend_req.birth_year_min is not None:
                query = query.filter(BasicHardware.birth_year >= friend_req.birth_year_min)
            if friend_req.birth_year_max is not None:
                query = query.filter(BasicHardware.birth_year <= friend_req.birth_year_max)
                
            if friend_req.height_min is not None:
                query = query.filter(BasicHardware.height >= friend_req.height_min)
            if friend_req.height_max is not None:
                query = query.filter(BasicHardware.height <= friend_req.height_max)
                
            # if friend_req.city:
            #     query = query.filter(BasicHardware.city.like(f"%{friend_req.city}%"))
                
            # 限制召回数量，避免一次给 LLM 塞太多数据
            return query.limit(20).all()
        finally:
            session.close()

    def save_match_result(self, match_result: MatchResult):
        session = self.mysql.get_session()
        try:
            # 检查是否已存在推荐（可选，避免重复推荐同一个人，或者允许更新）
            existing = session.query(MatchResult).filter(
                MatchResult.source_user == match_result.source_user,
                MatchResult.target_user == match_result.target_user
            ).first()
            
            if existing:
                existing.score = match_result.score
                existing.match_reason = match_result.match_reason
                session.commit()
                session.refresh(existing)
                return existing
            else:
                session.add(match_result)
                session.commit()
                session.refresh(match_result)
                return match_result
        except:
            session.rollback()
            raise
        finally:
            session.close()
