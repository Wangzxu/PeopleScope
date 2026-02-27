from langchain_core.messages import SystemMessage, AIMessage
from graph.state.basicHardwareState import BasicHardwareState
from core.model import LLMFactory


def info_friend_agent_node(state: BasicHardwareState):
    missing = state["friend_missing_fields"]
    messages = state["messages"]
    
    # 构造系统提示词
    system_prompt = f"""
        你是一个信息采集助手。我们现在需要采集用户期望找的朋友的 8 项基础信息。
        当前缺失期望朋友的字段：{missing}
    
        任务：
        1. 从缺失字段中选择一个最自然的进行追问。
        2. 请保持对话自然、友好，每次只追问一个问题，不要一次性问多个。
        3. 请在提问中明确表示你是在问关于用户期望的另一半（朋友）的要求。
        4. 如果所有信息都已经收集完毕，感谢用户的配合。
    """

    # 构造新的对话列表
    chat_history = [SystemMessage(content=system_prompt)] + messages

    # 调用大模型
    response = LLMFactory.get_model().invoke(chat_history)
    
    return {"messages": [AIMessage(content=response.content)]}
