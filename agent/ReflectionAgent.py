from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from core.logger import setup_logger
from core.agent import LLMType
from schema.relectionSchema import Reflection


class Traits(BaseModel):
    extroversion: int = Field(..., description="外向性 1~10")
    agreeableness: int = Field(..., description="宜人性 1~10")
    conscientiousness: int = Field(..., description="尽责性 1~10")
    neuroticism: int = Field(..., description="神经质 1~10")
    openness: int = Field(..., description="开放性 1~10")
    dominance: int = Field(..., description="支配性 1~10")
    empathy: int = Field(..., description="同理心 1~10")
    risk_taking: int = Field(..., description="冒险性 1~10")
    emotional_stability: int = Field(..., description="情绪稳定性 1~10")
    self_control: int = Field(..., description="自我控制 1~10")


class Output(BaseModel):
    summary: str = Field(..., description="根据过往用户画像，和现在问题的回答更新后的新用户总结")
    traits: Traits = Field(..., description="用户在十个维度上的评分向量")


class ReflectionAgent:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory
        self.system_prompt = """
        你是一个人格分析助手。
        
        你的任务：
        根据用户本次回答（reflection），
        生成一个更新后的 summary 和新的十维 trait 分数。
        
        输入信息：
        
        1. reflection：
        user: str = Field(..., description="用户ID")
        question: str = Field(..., description="问题内容")
        answer: str = Field(..., description="用户回答")
                
        要求：
        
        1. 输出严格为 JSON 格式：
        {
            "summary": "...更新后的总结...",
            "traits": {
                "extroversion": int(1~10),
                "agreeableness": int(1~10),
                "conscientiousness": int(1~10),
                "neuroticism": int(1~10),
                "openness": int(1~10),
                "dominance": int(1~10),
                "empathy": int(1~10),
                "risk_taking": int(1~10),
                "emotional_stability": int(1~10),
                "self_control": int(1~10)
            }
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

    def generate_reflection(self, reflection: Reflection):
        res = self.agent.invoke({
            "messages": [HumanMessage(content=f"根据本次问答{reflection}生成新的用户画像")]
        })
        logger = setup_logger()
        logger.info(f"反馈用户本次分析结果：{reflection.user}的本轮分析为: {res['structured_response']}")
        summary = res['structured_response'].summary
        traits = res['structured_response'].traits
        return summary, traits

