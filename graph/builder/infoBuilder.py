from langgraph.graph import StateGraph, END
from graph.nodes.stageTransitionNode import stage_transition_node
from graph.state.basicHardwareState import BasicHardwareState
from graph.nodes.checkStateNode import check_status_node
from graph.nodes.infoAgentNode import info_agent_node
from graph.nodes.extractInfoNode import extract_info_node
from graph.nodes.extractFriendInfoNode import extract_friend_info_node
from graph.nodes.infoFriendAgentNode import info_friend_agent_node
from graph.nodes.recommendationNode import recommendation_node

workflow = StateGraph(BasicHardwareState)

# 添加节点
workflow.add_node("extract_info", extract_info_node)
workflow.add_node("check_status", check_status_node)
workflow.add_node("info_agent", info_agent_node)

workflow.add_node("stage_transition_node", stage_transition_node)

workflow.add_node("extract_friend_info", extract_friend_info_node)
workflow.add_node("info_friend_agent", info_friend_agent_node)
workflow.add_node("recommendation_node", recommendation_node)


def router_node(state: BasicHardwareState):
    # 简单的透传节点，用于路由。返回空字典表示不对 state 进行任何更新，
    # 避免带有 operator.add 的字段（如 messages）发生内容翻倍的 bug。
    return {}


workflow.add_node("router", router_node)

# 设置入口: 先经过路由判断用户自身信息是否收集完毕
workflow.set_entry_point("router")


def route_start(state: BasicHardwareState):
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


workflow.add_conditional_edges(
    "router",
    route_start,
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

app = workflow.compile()
