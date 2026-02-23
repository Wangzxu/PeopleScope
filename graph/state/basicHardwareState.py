from typing import Annotated, List, TypedDict, Optional
import operator
from schema.hardwareSchema import BasicHardwareSchema



# 定义的 8 个硬件属性模型
class BasicHardwareState(TypedDict):
    # 存储已采集的硬件信息
    hardware_data: BasicHardwareSchema
    # 对话历史
    messages: Annotated[List[dict], operator.add]
    # 待采集的字段清单
    missing_fields: List[str]
    # 是否已完成采集
    is_complete: bool
