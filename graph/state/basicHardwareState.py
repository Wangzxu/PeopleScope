from typing import Annotated, List, TypedDict, Optional
import operator
from schema.hardwareSchema import BasicHardwareSchema, FriendHardwareSchema


# 定义的 8 个硬件属性模型，包含自身属性和期望朋友属性
class BasicHardwareState(TypedDict):
    # 存储已采集的硬件信息
    hardware_data: BasicHardwareSchema
    # 存储已采集的期望朋友的硬件信息
    friend_hardware_data: FriendHardwareSchema
    # 对话历史
    messages: Annotated[List[dict], operator.add]
    # 待采集的字段清单
    missing_fields: List[str]
    # 朋友待采集的字段清单
    friend_missing_fields: List[str]
    # 是否已完成自身采集
    is_complete: bool
    # 是否已完成朋友信息采集
    friend_is_complete: bool
