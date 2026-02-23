from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from core.model import LLMType
from core.logger import get_logger
from model.aggregation import AggregationModel

logger = get_logger(__name__)


class Output(BaseModel):
    summary: str = Field(..., description="根据过往用户画像，和过往问题的回答更新后的新用户总结")


class AggregateAgent:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory
        self.system_prompt = """
        你是一个人格分析助手。

        你的任务：
        根据用户的基础信息aggregate十维 trait 分数
        生成一个更新后的 summary 和新的。

        输入信息：

        1.  aggregate:
        id = Column(Integer, primary_key=True, autoincrement=True)
        user = Column(String(64), nullable=False)
    
        extroversion = Column(Integer, nullable=False)
        agreeableness = Column(Integer, nullable=False)
        conscientiousness = Column(Integer, nullable=False)
        neuroticism = Column(Integer, nullable=False)
        openness = Column(Integer, nullable=False)
        dominance = Column(Integer, nullable=False)
        empathy = Column(Integer, nullable=False)
        risk_taking = Column(Integer, nullable=False)
        emotional_stability = Column(Integer, nullable=False)
        self_control = Column(Integer, nullable=False)
    
        summary = Column(Text)

        要求：

        1. 输出严格为 JSON 格式：
        {
            "summary": "...更新后的总结...",
        }

        2. traits 的数值为整数 1~10，1 表示最低，10 表示最高。
        3. summary 应简明概括用户特征和变化。
        4. 仅输出 JSON，不要包含额外文字或解释。"""
        
        self.agent = self._create_agent()

    def _create_agent(self):
        return create_agent(
            model=self.llm_factory.get_model(LLMType.PRECISE),
            system_prompt=self.system_prompt,
            tools=[],
            response_format=ProviderStrategy(Output)
        )

    def generate_aggregate(self, aggregate: AggregationModel):
        res = self.agent.invoke({
            "messages": [HumanMessage(content=f"根据{aggregate}中十个维度的打分进行总结")]
        })
        logger.info(f"反馈用户本次分析结果：{aggregate.user}的本轮分析为: {res['structured_response']}")
        summary = res['structured_response'].summary
        return summary

