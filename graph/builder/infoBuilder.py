from langgraph.graph import StateGraph, END
from graph.state.basicHardwareState import BasicHardwareState
from graph.nodes.checkStateNode import check_status_node
from graph.nodes.infoAgentNode import info_agent_node
from graph.nodes.extractInfoNode import extract_info_node

workflow = StateGraph(BasicHardwareState)

# 添加节点
workflow.add_node("extract_info", extract_info_node)
workflow.add_node("check_status", check_status_node)
workflow.add_node("info_agent", info_agent_node)

# 设置入口: 先提取信息
workflow.set_entry_point("extract_info")

# 提取完信息后，检查状态
workflow.add_edge("extract_info", "check_status")

# 设置条件连线
workflow.add_conditional_edges(
    "check_status",
    lambda x: "complete" if x["is_complete"] else "continue",
    {
        "continue": "info_agent",
        "complete": END  # 已完成所有采集，结束
    }
)

# 形成单次交互：Agent 问完后直接结束，等待下次用户输入重新调用
workflow.add_edge("info_agent", END)

app = workflow.compile()