from core.logger import get_logger
from graph.state.basicHardwareState import BasicHardwareState


def check_status_node(state: BasicHardwareState):
    data = state["hardware_data"]

    logger = get_logger(__name__)
    # 调试日志：看看到底拿到了什么数据
    logger.info(f"DEBUG: Current Hardware Data: {data.model_dump()}")
    
    def is_missing(val):
        if val is None:
            return True
        if isinstance(val, str):
            val = val.strip()
            # 过滤掉空字符串或无意义的提取值
            if val in ["", "无", "未知", "不确定", "暂无", "不知道"]:
                return True
        return False
        
    # 找出所有缺失的字段名，排除不需要采集的 user 字段
    missing = [field for field, value in data.model_dump().items() if is_missing(value) and field != "user"]
    print(f"--- [DEBUG] 正在检查字段，缺失项为: {missing} ---")  # 增加这一行

    return {
        "missing_fields": missing,
        "is_complete": len(missing) == 0
    }
