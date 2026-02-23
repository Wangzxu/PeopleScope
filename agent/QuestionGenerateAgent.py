from typing import Union, List
from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from core.logger import get_logger
from core.model import LLMType
from model.question import QuestionTrait

logger = get_logger(__name__)


class Question(BaseModel):
    """单个问题"""
    question: str = Field(..., description="简短、清晰、不含专业术语的问题")
    trait: Union[int, str] = Field(..., description="分类标签，从1~10的数字")


class Output(BaseModel):
    """Agent最终输出格式 - 支持多个问题"""
    questions: List[Question] = Field(..., description="问题列表，每个问题测试一个不同维度")


TRAIT_INDEX = {
    "extroversion": 1,
    "agreeableness": 2,
    "conscientiousness": 3,
    "neuroticism": 4,
    "openness": 5,
    "dominance": 6,
    "empathy": 7,
    "risk_taking": 8,
    "emotional_stability": 9,
    "self_control": 10
}


class QuestionGenerateAgent:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory
        self.system_prompt = f"""
        你是一名心理测评专家。
        
        你的任务是：
        1. 生成多条【简短、清晰、不含专业术语】的人格测评问题
        2. 每个问题主要测试【一个且仅一个】人格维度
        3. 人格维度必须从以下列表中选择，不能重复维度，不能创造新维度：
        
        {TRAIT_INDEX}
        
        输出要求（必须严格遵守）：
        - 只输出 JSON
        - 不要解释
        - 不要多余文本
        - 不要编号
        
        JSON 格式如下：
            {{
              "questions": [
                {{"question": "问题1", "trait": 1}},
                {{"question": "问题2", "trait": 2}},
                ...
              ]
            }}
    """
        self.agent = self._create_agent()

    def _create_agent(self):
        return create_agent(
            model=self.llm_factory.get_model(LLMType.BALANCED),
            system_prompt=self.system_prompt,
            tools=[],
            response_format=ProviderStrategy(Output)
        )

    def generate_questions(self, number: int) -> List[QuestionTrait]:
        res = self.agent.invoke({
            "messages": [HumanMessage(content=f"生成{number}个问题")]
        })
        logger.info(f"生成{number}个问题")
        entity_list = []
        for q in res["structured_response"].questions:
            entity = QuestionTrait(
                question=q.question,
                trait_score=q.trait
            )
            entity_list.append(entity)
            logger.info(f"生成问题，Trait: {q.trait},question: {q.question}")
        return entity_list

