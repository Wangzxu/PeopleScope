from sqlalchemy.orm import Session
from core import logger
from repository.ReflectionRepository import ReflectionRepository
from core.config import TRAIT_FIELDS
from agent.AggregateAgent import generate_aggregate
from repository.AggregationRepository import AggregationRepository


logger = logger.setup_logger()


class AggregationService:
    @staticmethod
    def generate_aggregate(db: Session, user: str):
        aggregate = AggregationRepository.get_by_user(db, user=user)
        reflections = ReflectionRepository.list_by_user(db, user=user)
        n = len(reflections)
        alpha = 1 / (n + 1)
        for reflection in reflections:
            for trait in TRAIT_FIELDS:
                score = getattr(aggregate, trait)
                score = score * (1 - alpha) + reflection.traits[trait] * alpha
                setattr(aggregate, trait, score)
        logger.info(f"更新Traits参数成功")
        summary = generate_aggregate(aggregate)
        logger.info(f"生成新的summary：{summary}")
        aggregate.summary = summary
        return AggregationRepository.update(db, aggregate)

    @staticmethod
    def get_aggregate(db: Session, user: str):
        aggregate = AggregationRepository.get_by_user(db, user=user)
        return aggregate

