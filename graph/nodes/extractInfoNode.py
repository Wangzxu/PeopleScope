from langchain_core.messages import SystemMessage, ToolMessage
from graph.state.basicHardwareState import BasicHardwareState
from core.model import LLMFactory
from schema.hardwareSchema import HardwareUpdate


def extract_info_node(state: BasicHardwareState):
    messages = state["messages"]
    hardware_data = state["hardware_data"]

    # 获取模型
    llm = LLMFactory.get_extract_model().bind_tools([HardwareUpdate])

    # 构造系统提示词
    system_prompt = f"""
        你是一个信息提取助手。我们需要采集用户的 8 项基础信息。
        用户已提供的信息：{hardware_data.model_dump(exclude_none=True)}
    
        任务：
        1. 分析用户的最新输入。如果用户提供了关于自身的、属于上述 8 项基础信息中的任何一项，请调用工具 `HardwareUpdate` 进行提取。
        2. 【严禁脑补】只提取用户在最新回复中明确提供的确切信息。如果用户没有提到某个字段，在调用工具时绝对不要包含该字段（不要传空字符串、不要传0、不要传"未知"）。
        3. 如果用户的输入没有包含任何有用的基础信息，请不要调用工具。
        4. 你只需要提取信息，不需要回复用户文本。
    """
    
    # 获取最后一条用户消息进行提取
    context_messages = messages[-2:]

    # 2. 扁平化列表拼接（确保 chat_history 是 List[BaseMessage]）
    chat_history = [SystemMessage(content=system_prompt)] + context_messages

    # 3. 调用模型
    response = llm.invoke(chat_history)
        
    updated_data = hardware_data.model_copy()

    # 如果有工具调用，更新数据
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == "HardwareUpdate":
                args = tool_call["args"]
                for key, value in args.items():
                    if value is not None and key in updated_data.model_dump():
                        setattr(updated_data, key, value)
                            
    return {"hardware_data": updated_data}
