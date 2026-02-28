from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, AIMessage
from graph.state.basicHardwareState import BasicHardwareState
from core.model import LLMFactory


class FriendInfoCollectionStatus(BaseModel):
    is_complete: bool = Field(...,
                              description="是否判断用户对朋友的所有期望条件都已表达到位。如果用户明确表示其他没要求，或基本核心项已涵盖且用户无继续补充意愿，则为True。")
    reply_message: str = Field(...,
                               description="如果未收集完毕(is_complete=False)，请生成一条自然、友好的追问，每次只问一个缺失的问题。如果已收集完("
                                           "is_complete=True)，给出一句简短的过渡语(如'好的，要求我都记下了，马上为你匹配...')。")


def info_friend_agent_node(state: BasicHardwareState):
    data = state["friend_hardware_data"]
    messages = state["messages"]
    hardware = state["hardware_data"]

    def is_missing(val):
        if val is None:
            return True
        if isinstance(val, str):
            val = val.strip()
            # 如果提取到了空字符串，或者"未知"，则在物理层面上视为没收集到。
            if val in ["", "未知", "不知道"]:
                return True
        return False

    # 找出所有缺失的字段名，排除不需要采集的 user 字段，作为提示给大模型参考
    missing = [field for field, value in data.model_dump().items() if is_missing(value) and field != "user"]

    # 构造系统提示词
    system_prompt = f"""
        你是一个专业的红娘和信息采集助手。你需要判断当前用户对于【期望的另一半/朋友】的要求是否已经收集完毕，并决定下一步的回复。
        
        当前已收集到的期望条件（物理层面）：
        {data.model_dump(exclude_none=True)}
        
        目前在我们的标准模板中仍为空的字段有：{missing}
        
        【任务与判断规则】：
        1. 结合聊天上下文，判断用户是否已经表达完了他们的主要诉求。
        2. 如果用户明确说“其他没要求”、“就这些”、“看感觉”等，或者核心信息已经收集得差不多且用户没有继续补充的意图，那么即使 `missing` 列表不为空，你也应该认为收集结束！此时将 `is_complete` 设为 True，并在 `reply_message` 中给出一句简短的感谢和过渡语（不要再提问了）。
        3. 如果用户还在正常交流，并且 `missing` 列表中还有维度可以挖掘，则将 `is_complete` 设为 False，并在 `reply_message` 中从缺失字段中挑选【一个】最自然的话题进行追问。
        
        【严禁事项（非常重要）】：
        - 你的 `reply_message` 必须【只包含】你当前要说的那一句新话，绝对不要重复或包含之前的对话历史！
        - 绝对不要输出类似 "上一句: xxx" 或 "我说过: xxx" 这样的前缀。
        - 直接、自然地问出你的新问题即可。
        - 每次【绝对只追问一个问题】，严禁并列提问。
        - 每次提问仅对{missing}的字段进行追问，对已经填写的内容不作追问
    """

    # 构造新的对话列表，过滤掉当前轮次可能已经附加的AI消息（如stage_transition_node生成的过渡语），
    # 防止大模型看到最后一条是AI消息时，误以为需要续写或重写它，从而造成重复输出。
    last_human_idx = -1
    for i in range(len(messages) - 1, -1, -1):
        if messages[i].type == 'human':
            last_human_idx = i
            break
            
    if last_human_idx != -1:
        filtered_messages = messages[:last_human_idx + 1]
    else:
        filtered_messages = messages
    
    chat_history = [SystemMessage(content=system_prompt)] + filtered_messages

    # 调用大模型
    llm = LLMFactory.get_model().with_structured_output(FriendInfoCollectionStatus)
    response = llm.invoke(chat_history)

    return {"messages": [AIMessage(content=response.reply_message)],
            "friend_missing_fields": missing,
            "friend_is_complete": response.is_complete
            }
