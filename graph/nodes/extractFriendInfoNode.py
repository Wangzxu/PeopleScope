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
        # Role
        你是一个社交意图提取专家，负责将用户的口语描述转化为数据库匹配字段。
        
        # Reference (用户自身信息)
        这是当前用户的资料，当用户提到“和我一样/类似”时，请查询此数据进行换算：
        {hardware_data}
        
        # Output Logic
        你的唯一任务是调用工具 `FriendHardwareUpdate`。
        1. **数值转化**：严禁输出“180cm左右”这类字符串。必须转化为数值区间。
           - 用户：“我1995的，找个差不多的。” -> 提取：birth_year_min=1992, birth_year_max=1998。
        2. **学历对齐**：用户：“学历一样。” -> 查看参考信息为硕士(4) -> 提取：education=4。
        3. **主体判定**：若用户说“我是上海人”，这是在描述自己，【不要】调用工具更新朋友资料。
        
        # Constraints
        - 禁止回复任何文字。
        - 只提取明确提及或参照的信息。
    """
    
    # 获取最后一条用户消息进行提取
    context_messages = messages[-2:]
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
