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
        Role
        你是一个社交意图提取专家，负责将用户的口语描述转化为数据库匹配字段 FriendHardwareUpdate。
        
        Reference (用户自身信息 - 只读受限模式)
        警告：以下数据仅作为【逻辑换算】的字典，严禁直接将其作为默认值填充到要求中。
        {hardware_data}
        
        Output Logic
        你的唯一任务是调用工具 FriendHardwareUpdate。请遵循以下严格的提取逻辑：
        
        显式触发原则（核心修复）：
        
        禁止主动填充：如果用户未提及某个维度（如：没提身高），对应的字段必须保持为 null，绝对禁止参考用户自身身高进行填充。
        
        仅限参照提取：只有当用户明确表达“和我一样”、“跟我差不多”、“同上”时，才允许检索【用户自身信息】并进行数值转化。
        
        数值转化规范：
        
        严禁输出“180cm左右”等模糊字符串，必须转化为具体的数值。
        
        参照换算示例：
        
        用户：“年龄和我差不多” -> 检索用户出生年(1995) -> 提取：birth_year_min=1992, birth_year_max=1998。
        
        用户：“身高比我高点” -> 检索用户身高(170) -> 提取：height_min=172。
        
        主体隔离：
        
        严格区分“自我描述”与“对他要求”。
        
        若用户说“我是上海人”，这是在更正自身信息，严禁调用 FriendHardwareUpdate 工具。
        
        只有当用户在描述“想找的人”时，才触发工具调用。
        
        处理“无所谓”：
        
        若用户明确说“没要求”、“看感觉”、“不限”，该字段应填入字符串 "不限"（若字段允许）或保持 null，不要根据用户自身的优秀程度去脑补“对方也该如此”。
        
        Constraints
        禁止回复任何文字，仅输出工具调用。
        
        严禁脑补：未提及的信息 = null。
        
        逻辑优先：用户口头表达 > 你的常识推断。
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
