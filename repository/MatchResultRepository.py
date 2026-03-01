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

    def delete_matches_by_user(self, source_user: str):
        """删除某个用户发起的所有旧匹配结果"""
        session = self.mysql.get_session()
        try:
            session.query(MatchResult).filter(MatchResult.source_user == source_user).delete()
            session.commit()
        except:
            session.rollback()
            raise
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
                
            unique_matches = []
            seen_users = set()
            for match, hardware in results:
                if match.target_user not in seen_users:
                    seen_users.add(match.target_user)
                    unique_matches.append({
                        "match": match,
                        "hardware": hardware
                    })
                    
            return unique_matches
        finally:
            session.close()

    def get_candidates(self, friend_req: FriendHardwareSchema) -> List[BasicHardware]:
        session = self.mysql.get_session()
        try:
            # 基础过滤：排除当前用户
            query = session.query(BasicHardware).filter(BasicHardware.user != friend_req.user)
            
            # 以下为可选过滤条件，根据 friend_hardware_data 进行筛选
            if friend_req.birth_year_min is not None:
                query = query.filter(BasicHardware.birth_year >= friend_req.birth_year_min)
            if friend_req.birth_year_max is not None:
                query = query.filter(BasicHardware.birth_year <= friend_req.birth_year_max)
                
            if friend_req.height_min is not None:
                query = query.filter(BasicHardware.height >= friend_req.height_min)
            if friend_req.height_max is not None:
                query = query.filter(BasicHardware.height <= friend_req.height_max)
                
            # 限制召回数量，避免一次给 LLM 塞太多数据
            raw_candidates = query.limit(40).all()
            
            unique_candidates = []
            seen_users = set()
            for cand in raw_candidates:
                if cand.user not in seen_users:
                    seen_users.add(cand.user)
                    unique_candidates.append(cand)
                    if len(unique_candidates) == 20: # 最终保留20个去重后的候选人
                        break
                        
            return unique_candidates
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
