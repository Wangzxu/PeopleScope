from pydantic import BaseModel, Field
from typing import Optional


class BasicHardwareSchema(BaseModel):
    user: Optional[str] = Field(None, description="用户名")
    birth_year: Optional[int] = Field(None, description="出生年份，如1998")
    height: Optional[int] = Field(None, description="身高，单位cm")
    city: Optional[str] = Field(None, description="目前常住的城市")
    education: Optional[str] = Field(None, description="最高学历")
    occupation: Optional[str] = Field(None, description="职业或所在行业")
    income_level: Optional[str] = Field(None, description="大致的年薪范围")
    smoking_drinking: Optional[str] = Field(None, description="烟酒偏好描述")
    hometown: Optional[str] = Field(None, description="籍贯或家乡背景")


class HardwareUpdate(BaseModel):
    """用于更新用户缺失的硬件属性信息。如果用户提到了相关信息，请提取。"""
    birth_year: Optional[int] = Field(None, description="出生年份，如1998")
    height: Optional[int] = Field(None, description="身高，单位cm")
    city: Optional[str] = Field(None, description="目前常住的城市")
    education: Optional[str] = Field(None, description="最高学历")
    occupation: Optional[str] = Field(None, description="职业或所在行业")
    income_level: Optional[str] = Field(None, description="大致的年薪范围")
    smoking_drinking: Optional[str] = Field(None, description="烟酒偏好描述")
    hometown: Optional[str] = Field(None, description="籍贯或家乡背景")