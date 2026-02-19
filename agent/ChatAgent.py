from langchain.agents import create_agent
from langchain.agents.structured_output import ProviderStrategy
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import InMemorySaver
from pydantic import BaseModel, Field
from core.agent import LLMType


class Output(BaseModel):
    answer: str = Field(..., description="根据过往用户画像和现在问题的回答")


SYSTEM_PROMPT_TEMPLATE = """
        你是一个长期陪伴用户的对话型 AI 助手。
        
        【你的目标】
        在保持当前会话主题一致的前提下，
        根据用户的稳定偏好，生成符合其聊天风格和兴趣的回复。
        
        【用户画像信息】
        - 用户名：{user}
        - 用户偏好聊天风格标签：{style_tags}
        - 用户偏好聊天主题标签：{topic_tags}
        
        【相关历史对话】
        以下是用户过去与当前问题最相关的几条发言，可作为参考：
        {related_chats}
        
        【当前会话信息】
        - 当前会话主题（title）：{title}
        
        【回复规则】
        1. 回复风格必须贴合 style_tags
        2. 回复内容尽量贴合 topic_tags，除非用户明确偏离
        3. 保持自然对话感，不要暴露“标签”“画像”等系统概念
        4. 如果用户问题模糊，可适度引导澄清
        5. 不要过度说教，不要无关扩展
        
        【输出要求】
        - 使用中文
        - 直接输出回复内容，不要解释你的思考过程
        请严格按照以下 JSON 格式输出，不要包含任何多余解释文本：
        
        {{
          "answer": 具体输出内容
        }}
"""

class ChatAgent:
    def __init__(self, llm_factory):
        self.llm_factory = llm_factory
        self.checkpointer = InMemorySaver()

    def _create_chat_agent(self, system_prompt: str):
        return create_agent(
            model=self.llm_factory.get_model(LLMType.CREATIVE),
            system_prompt=system_prompt,
            tools=[],
            response_format=ProviderStrategy(Output),
            checkpointer=self.checkpointer
        )

    def generate_answer(
        self,
        title: str,
        user: str,
        tags: str,
        message: str,
        session_id: int,
        related_chats: list = None
    ) -> str:
        
        related_chats_str = "\n".join(related_chats) if related_chats else "无"

        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            user=user,
            style_tags=tags["style"],
            topic_tags=tags["topic"],
            related_chats=related_chats_str,
            title=title
        )

        agent = self._create_chat_agent(system_prompt)

        config = {
            "configurable": {
                "thread_id": session_id
            }
        }

        res = agent.invoke(
            {"messages": [HumanMessage(content=message)]},
            config=config
        )

        return res["structured_response"].answer


