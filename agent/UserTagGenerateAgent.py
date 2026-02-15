from typing import List

from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from core.logger import setup_logger
from core.container import db_container
from core.agent import LLMType
from model.aggregation import AggregationModel


class Output(BaseModel):
    style_tags: List[str]
    topic_tags: List[str]


system_prompt = """
        你是一个用户画像分析 Agent，负责从有限信息中推断用户的聊天偏好标签。
        
        【任务目标】
        根据给定的用户人格 traits 总结，以及该用户所有历史 session 的主题，
        推断用户偏好的：
        1. 聊天风格标签（如：简洁、详细、幽默、理性、结构化等）
        2. 聊天主题标签（如：技术、学习、情感、职业规划、效率工具等）
        
        【已知信息】
        
        用户人格 traits 总结：
        {summary}
        
        用户最近会话记录 conv 列表：
        {conv}
        
        【推断规则】
        - 只根据给定信息进行推断，不要凭空编造
        - 标签应为“稳定偏好”，而非偶然行为
        - 聊天风格标签重点结合 traits
        - 聊天主题标签重点结合 conv 主题的重复性和集中度
        - 每一类标签数量控制在 3~5 个
        - 使用简短、通用、可复用的中文关键词
        
        【输出要求】
        请严格按照以下 JSON 格式输出，不要包含任何多余解释文本：
        
        {
          "style_tags": ["标签1", "标签2", "标签3"],
          "topic_tags": ["标签1", "标签2", "标签3"]
        }
        """

agent = create_agent(
    model=db_container.get_model().get_model(LLMType.PRECISE),
    system_prompt=system_prompt,
    tools=[],
    response_format=ProviderStrategy(Output)
)


def generate_tag(conv: List[str], summary: str, title: List[str]):
    res = agent.invoke({
        "messages": [HumanMessage(content=f"根据用户的性格{summary}和会话记录{conv},以及几个会话的主题{title}，推测用户喜欢的聊天风格和聊天内容")]
    })
    logger = setup_logger()
    logger.info(f"反馈用户本次分析结果: {res['structured_response']}")
    style_tags = res['structured_response'].style_tags
    topic_tags = res['structured_response'].topic_tags
    return style_tags, topic_tags
