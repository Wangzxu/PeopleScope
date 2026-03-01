from langchain_core.messages import SystemMessage, AIMessage
from graph.state.basicHardwareState import BasicHardwareState


class InfoAgentNode:
    def __init__(self, llm):
        self.llm = llm

    def __call__(self, state: BasicHardwareState):
        missing = state["missing_fields"]
        messages = state["messages"]
        
        # 构造系统提示词
        system_prompt = f"""
            你是一个信息采集助手。我们需要采集用户的 8 项基础信息。
            当前缺失字段：{missing}
        
            # Goal
            必须从上述缺失信息中挑选【一项】，以极其自然、日常聊天的口吻向用户发起追问。
            
            # Rules
            1. **强制追问**：当前节点被触发，说明信息采集【未结束】。禁止说“感谢配合”、“资料已齐”或任何结语。
            2. **单一任务**：每次只问一个问题。严禁并列提问（如：不要问“你多高？在哪工作？”）。
            3. **社交拟人化**：不要像审讯员。
               - 错误示例：“请提供你的年薪。”
               - 正确示例：“聊了这么多，还不知道你平时的职业领域大概是哪一块呢？”
            4. **禁止幻觉**：即使对话历史中提到过模糊的相关词，只要它在“缺失列表”中，就必须以确认的口吻重新追问。
            5. **禁止提前结束**：结束询问以缺失字段为准，直到缺失字段为空才停止继续询问，不然需要对缺失字段{missing}继续提问，不管之前是否询问过相关问题。
            
            # Output Requirement
            直接输出你的追问话术，不要带任何前缀（如“好的”、“我的建议是”等）。
        """
    
        # 构造新的对话列表
        chat_history = [SystemMessage(content=system_prompt)] + messages
    
        # 调用大模型
        response = self.llm.invoke(chat_history)
        
        return {"messages": [AIMessage(content=response.content)]}
