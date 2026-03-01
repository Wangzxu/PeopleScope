from langchain_core.messages import AIMessage

from graph.state.basicHardwareState import BasicHardwareState


class StageTransitionNode:
    def __call__(self, state: BasicHardwareState):
        # 构造转场话术
        welcome_msg = AIMessage(content=(
            "太棒了！你的个人基本信息我已经全部记录好啦。✨\n"
            "接下来，咱们聊聊你理想中的另一半吧？你希望 TA 是个什么样的人？"
            "（比如身高、年龄范围，或者是在哪个城市工作等等）"
        ))
    
        # 可以在这里更新一个 stage 标识位（如果你的 state 里有定义的话）
        # return {"messages": [welcome_msg], "stage": "friend"}
        return {"messages": [welcome_msg]}


# 在 Workflow 中：
# check_status (complete) -> stage_transition_node -> extract_friend_info
