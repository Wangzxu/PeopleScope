from graph.state.basicHardwareState import BasicHardwareState


def check_friend_status_node(state: BasicHardwareState):
    data = state["friend_hardware_data"]
    
    def is_missing(val):
        if val is None:
            return True
        if isinstance(val, str):
            val = val.strip()
            # 对于期望朋友的指标，用户可能会明确说"不限"或"无要求"，这种应该视为已收集到（不限也是一种要求）
            # 但是如果提取到了空字符串，或者"未知"，则视为没收集到。
            if val in ["", "未知", "不知道"]:
                return True
        return False
        
    # 找出所有缺失的字段名，排除不需要采集的 user 字段
    missing = [field for field, value in data.model_dump().items() if is_missing(value) and field != "user"]

    return {
        "friend_missing_fields": missing,
        "friend_is_complete": len(missing) == 0
    }
