from enum import Enum
from langchain.chat_models import init_chat_model
from core.config import OPENAI_API_KEY


class LLMType(Enum):
    PRECISE = 0.0  # 严谨、逻辑提取
    BALANCED = 0.5  # 平衡、通用
    CREATIVE = 0.8  # 创意、聊天


class LLMFactory:
    @staticmethod
    def get_model(llm_type: LLMType = LLMType.BALANCED):
        return init_chat_model(
            model="deepseek-ai/DeepSeek-V3.2",
            model_provider="openai",
            base_url="https://api.siliconflow.cn/v1",  # 官方域名
            temperature=llm_type.value,
            api_key=OPENAI_API_KEY
        )
