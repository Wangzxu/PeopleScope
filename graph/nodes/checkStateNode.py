from graph.state.basicHardwareState import BasicHardwareState


def check_status_node(state: BasicHardwareState):
    data = state["hardware_data"]
    # 找出所有值为 None 的字段名，排除不需要采集的 user 字段
    missing = [field for field, value in data.model_dump().items() if value is None and field != "user"]

    return {
        "missing_fields": missing,
        "is_complete": len(missing) == 0
    }
