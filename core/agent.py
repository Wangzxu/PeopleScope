from langchain.chat_models import init_chat_model
from core.config import OPENAI_API_KEY


model = init_chat_model(
    model="deepseek-ai/DeepSeek-V3.2",
    model_provider="openai",
    base_url="https://api.siliconflow.cn/v1",  # 官方域名
    temperature=0,
    api_key=OPENAI_API_KEY
)


def get_model():
    return model
