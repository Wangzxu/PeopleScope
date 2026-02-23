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
        1. 检查用户的最新输入，如果包含上述 8 项基础信息中的任何一项，请必须调用工具 `HardwareUpdate` 进行提取。
        2. 如果没有提取到任何信息，请不要调用工具。
        3. 你只需要提取信息，不需要回复用户。
    """
    
    # 使用最后一条用户消息进行提取
    if messages and messages[-1].type == 'human':
        last_message = messages[-1]
        chat_history = [SystemMessage(content=system_prompt), last_message]
        
        # 调用大模型
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
    
    return {}
