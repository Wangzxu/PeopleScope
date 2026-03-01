from langgraph.graph import StateGraph, END
from graph.state.basicHardwareState import BasicHardwareState


class InfoGraphBuilder:
    def __init__(self, extract_info_node, check_status_node, info_agent_node, 
                 stage_transition_node, extract_friend_info_node, 
                 info_friend_agent_node, recommendation_node):
        self.extract_info_node = extract_info_node
        self.check_status_node = check_status_node
        self.info_agent_node = info_agent_node
        self.stage_transition_node = stage_transition_node
        self.extract_friend_info_node = extract_friend_info_node
        self.info_friend_agent_node = info_friend_agent_node
        self.recommendation_node = recommendation_node

    def router_node(self, state: BasicHardwareState):
        # 简单的透传节点，用于路由。返回空字典表示不对 state 进行任何更新，
        # 避免带有 operator.add 的字段（如 messages）发生内容翻倍的 bug。
        return {}

    def route_start(self, state: BasicHardwareState):
        data = state["hardware_data"]
    
        def is_missing(val):
            if val is None:
                return True
            if isinstance(val, str):
                val = val.strip()
                if val in ["", "无", "未知", "不确定", "暂无", "不知道"]:
                    return True
            return False
    
        missing = [field for field, value in data.model_dump().items() if is_missing(value) and field != "user"]
        if len(missing) == 0:
            return "extract_friend_info"
        return "extract_info"

    def build(self):
        workflow = StateGraph(BasicHardwareState)
        
        # 添加节点
        workflow.add_node("extract_info", self.extract_info_node)
        workflow.add_node("check_status", self.check_status_node)
        workflow.add_node("info_agent", self.info_agent_node)
        
        workflow.add_node("stage_transition_node", self.stage_transition_node)
        
        workflow.add_node("extract_friend_info", self.extract_friend_info_node)
        workflow.add_node("info_friend_agent", self.info_friend_agent_node)
        workflow.add_node("recommendation_node", self.recommendation_node)
        
        workflow.add_node("router", self.router_node)
        
        # 设置入口: 先经过路由判断用户自身信息是否收集完毕
        workflow.set_entry_point("router")
        
        workflow.add_conditional_edges(
            "router",
            self.route_start,
            {
                "extract_info": "extract_info",
                "extract_friend_info": "extract_friend_info"
            }
        )
        
        # 第一阶段：提取自身信息后，检查状态
        workflow.add_edge("extract_info", "check_status")
        
        # 设置条件连线
        workflow.add_conditional_edges(
            "check_status",
            lambda x: "complete" if x["is_complete"] else "continue",
            {
                "continue": "info_agent",
                "complete": "stage_transition_node"  # 已完成自身采集，进入朋友信息采集阶段
            }
        )
        
        # 形成单次交互：Agent 问完后直接结束，等待下次用户输入重新调用
        workflow.add_edge("info_agent", END)
        workflow.add_edge("stage_transition_node", END)
        
        # 4. 第二阶段连线
        workflow.add_edge("extract_friend_info", "info_friend_agent")
        
        workflow.add_conditional_edges(
            "info_friend_agent",
            lambda x: "complete" if x.get("friend_is_complete") else "continue",
            {
                "continue": END,
                "complete": "recommendation_node"  # 已完成所有采集，进入推荐环节
            }
        )
        
        workflow.add_edge("recommendation_node", END)
        
        return workflow.compile()
