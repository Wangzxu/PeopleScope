from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from core.agent import LLMType


class Output(BaseModel):
    title: str = Field(..., description="生成的简短讨论主题")


SYSTEM_PROMPT = """
    你是一个能够从文本中提取对话主题的智能助手。
    你的目标是根据用户提供的输入文本，生成一个简短、精炼的讨论主题（Title）。
    
    【要求】
    1. 主题应当简短，最好在 4-10 个字之间。
    2. 能够准确概括输入文本的核心意图或内容。
    3. 使用中文。
    4. 不要包含“主题：”等前缀，直接输出主题内容。
    
    【输出要求】
        请严格按照以下 JSON 格式输出，不要包含任何多余解释文本：
        
        {
          "title": "讨论主题"
        }

"""


class TitleGenerateAgent:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory
        self.system_prompt = SYSTEM_PROMPT
        self.agent = self._create_agent()

    def _create_agent(self):
        return create_agent(
            model=self.llm_factory.get_model(LLMType.PRECISE),
            system_prompt=self.system_prompt,
            tools=[],
            response_format=ProviderStrategy(Output)
        )

    def get_title(self, text: str) -> str:
        """
        根据输入的文本生成一个简短的讨论主题。
        :param text: 输入的文本内容
        :return: 简短的主题字符串
        """
        res = self.agent.invoke({
            "messages": [HumanMessage(content=text)]
        })
        return res["structured_response"].title

