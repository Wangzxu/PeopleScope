from langchain_core.messages import SystemMessage, ToolMessage
from graph.state.basicHardwareState import BasicHardwareState
from core.model import LLMFactory
from schema.hardwareSchema import FriendHardwareUpdate


def extract_friend_info_node(state: BasicHardwareState):
    messages = state["messages"]
    friend_hardware_data = state["friend_hardware_data"]
    hardware_data = state["hardware_data"]

    # 获取模型
    llm = LLMFactory.get_extract_model().bind_tools([FriendHardwareUpdate])

    # 构造系统提示词
    system_prompt = f"""
        你是一个专业的信息提取助手，专注于分析用户对“未来另一半”或“期望朋友”的要求。
        
        ### 核心背景
        用户自身的基础信息如下（作为参考，用于处理“和我一样”等表述）：
        {hardware_data}
        
        当前已提取到的朋友要求：
        {friend_hardware_data.model_dump(exclude_none=True)}
        
        ### 任务指令
        1. **识别语义对齐**：如果用户表达“和我差不多”、“跟我一样”、“和我类似”，请参考上述【用户自身信息】，提取对应数值填入 `FriendHardwareUpdate`。
           - 示例：用户说“身高跟我差不多”，参考用户身高180cm，提取结果为“180cm左右”。
           - 示例：用户说“学历一样就行”，参考用户学历为硕士，提取结果为“硕士”。
        2. **区分主体**：严格区分用户是在描述“自己”还是在提“对朋友的要求”。只有涉及对【朋友/另一半】的要求时才调用工具。
        3. **严禁脑补**：
           - 只提取明确提及或明确参照的信息。
           - 未提及的字段严禁包含在工具调用中（不要传“未知”、“不限”）。
           - 只有用户明确说“没要求”或“不限”时，对应字段才填“不限”。
        4. **上下文关联**：结合之前的 AI 提问和用户回答进行综合判定。
        
        你只需要调用工具进行提取，严禁回复任何文本。
    """
    
    # 使用最后一条用户消息进行提取
    if messages and messages[-1].type == 'human':
        # 1. 动态获取上下文：如果只有一条消息就取一条，有两条或以上就取最后两条
        context_messages = messages[-2:]

        # 2. 扁平化列表拼接（确保 chat_history 是 List[BaseMessage]）
        chat_history = [SystemMessage(content=system_prompt)] + context_messages

        # 调用大模型
        response = llm.invoke(chat_history)
        
        updated_data = friend_hardware_data.model_copy()

        # 如果有工具调用，更新数据
        if response.tool_calls:
            for tool_call in response.tool_calls:
                if tool_call["name"] == "FriendHardwareUpdate":
                    args = tool_call["args"]
                    for key, value in args.items():
                        if value is not None and key in updated_data.model_dump():
                            setattr(updated_data, key, value)
                            
        return {"friend_hardware_data": updated_data}
    
    return {}
