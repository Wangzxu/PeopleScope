from pydantic import BaseModel, Field
from typing import Optional


class BasicHardwareSchema(BaseModel):
    user: Optional[str] = Field(None, description="用户名")
    birth_year: Optional[int] = Field(None, description="出生年份，如1998")
    height: Optional[int] = Field(
        None,
        description="身高数字，单位cm。示例：175。如果是'一米八'请转为180"
    )
    city: Optional[str] = Field(
        None,
        description="常住城市。建议格式：'城市-区域'。示例：'上海-浦东'、'杭州-余杭'"
    )
    education: Optional[str] = Field(
        None,
        description="最高学历。示例：'本科'、'硕士(海外)'、'博士'"
    )
    occupation: Optional[str] = Field(
        None,
        description="职业或行业。示例：'互联网-产品经理'、'金融-券商分析师'"
    )
    income_level: Optional[str] = Field(
        None,
        description="年薪范围。示例：'20w-30w'、'50w+'、'15k/月'"
    )
    smoking_drinking: Optional[str] = Field(
        None,
        description="烟酒偏好。示例：'不抽烟不喝酒'、'偶尔社交饮酒'、'抽烟'"
    )
    hometown: Optional[str] = Field(
        None,
        description="籍贯/家乡。示例：'江苏苏州'、'东北地区'、'广东深圳'"
    )


class HardwareUpdate(BaseModel):
    """用于更新用户缺失的硬件属性信息。如果用户提到了相关信息，请提取。"""
    birth_year: Optional[int] = Field(None, description="出生年份，如1998")
    height: Optional[int] = Field(
        None,
        description="身高数字，单位cm。示例：175。如果是'一米八'请转为180"
    )
    city: Optional[str] = Field(
        None,
        description="常住城市。建议格式：'城市-区域'。示例：'上海-浦东'、'杭州-余杭'"
    )
    education: Optional[str] = Field(
        None,
        description="最高学历。示例：'本科'、'硕士(海外)'、'博士'"
    )
    occupation: Optional[str] = Field(
        None,
        description="职业或行业。示例：'互联网-产品经理'、'金融-券商分析师'"
    )
    income_level: Optional[str] = Field(
        None,
        description="年薪范围。示例：'20w-30w'、'50w+'、'15k/月'"
    )
    smoking_drinking: Optional[str] = Field(
        None,
        description="烟酒偏好。示例：'不抽烟不喝酒'、'偶尔社交饮酒'、'抽烟'"
    )
    hometown: Optional[str] = Field(
        None,
        description="籍贯/家乡。示例：'江苏苏州'、'东北地区'、'广东深圳'"
    )


class FriendHardwareSchema(BaseModel):
    user: Optional[str] = Field(None, description="用户名")
    birth_year: Optional[str] = Field(None, description="期望的出生年份或范围")
    height: Optional[int] = Field(
        None,
        description="身高数字，单位cm。示例：175。如果是'一米八'请转为180"
    )
    city: Optional[str] = Field(
        None,
        description="常住城市。建议格式：'城市-区域'。示例：'上海-浦东'、'杭州-余杭'"
    )
    education: Optional[str] = Field(
        None,
        description="最高学历。示例：'本科'、'硕士(海外)'、'博士'"
    )
    occupation: Optional[str] = Field(
        None,
        description="职业或行业。示例：'互联网-产品经理'、'金融-券商分析师'"
    )
    income_level: Optional[str] = Field(
        None,
        description="年薪范围。示例：'20w-30w'、'50w+'、'15k/月'"
    )
    smoking_drinking: Optional[str] = Field(
        None,
        description="烟酒偏好。示例：'不抽烟不喝酒'、'偶尔社交饮酒'、'抽烟'"
    )
    hometown: Optional[str] = Field(
        None,
        description="籍贯/家乡。示例：'江苏苏州'、'东北地区'、'广东深圳'"
    )


class FriendHardwareUpdate(BaseModel):
    """用于更新用户缺失的期望朋友的硬件属性信息。如果用户提到了相关信息，请提取。"""
    birth_year: Optional[str] = Field(None, description="期望的出生年份或范围")
    height: Optional[int] = Field(
        None,
        description="身高数字，单位cm。示例：175。如果是'一米八'请转为180"
    )
    city: Optional[str] = Field(
        None,
        description="常住城市。建议格式：'城市-区域'。示例：'上海-浦东'、'杭州-余杭'"
    )
    education: Optional[str] = Field(
        None,
        description="最高学历。示例：'本科'、'硕士(海外)'、'博士'"
    )
    occupation: Optional[str] = Field(
        None,
        description="职业或行业。示例：'互联网-产品经理'、'金融-券商分析师'"
    )
    income_level: Optional[str] = Field(
        None,
        description="年薪范围。示例：'20w-30w'、'50w+'、'15k/月'"
    )
    smoking_drinking: Optional[str] = Field(
        None,
        description="烟酒偏好。示例：'不抽烟不喝酒'、'偶尔社交饮酒'、'抽烟'"
    )
    hometown: Optional[str] = Field(
        None,
        description="籍贯/家乡。示例：'江苏苏州'、'东北地区'、'广东深圳'"
    )
