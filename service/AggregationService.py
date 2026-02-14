from core import logger
from core.config import TRAIT_FIELDS
from agent.AggregateAgent import generate_aggregate
from repository.AggregationRepository import AggregationRepository
from repository.ReflectionRepository import ReflectionRepository

logger = logger.setup_logger()


class AggregationService:
    def __init__(self, agg_repo: AggregationRepository, reflection_repo: ReflectionRepository):
        self.agg_repo = agg_repo
        self.reflection_repo = reflection_repo

    def generate_aggregate(self, user: str):
        aggregate = self.agg_repo.get_by_user(user)
        reflections = self.reflection_repo.list_by_user(user)
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
        return self.agg_repo.update(aggregate)

    def get_aggregate(self, user: str):
        aggregate = self.agg_repo.get_by_user(user)
        return aggregate
