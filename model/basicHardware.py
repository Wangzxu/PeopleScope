from sqlalchemy import Column, Integer, String
from core.db.mysql import Base


class BasicHardware(Base):
    __tablename__ = "hardware"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")
    # 基础数值指标
    birth_year = Column(Integer, comment="出生年份，示例: 1998")
    height = Column(Integer, comment="身高(cm)，示例: 175")

    # 地域与背景
    city = Column(String(128), comment="常住城市，示例: '上海市' 或 '杭州市'")
    hometown = Column(String(128), comment="籍贯背景，示例: '山东青岛' 或 '新疆昌吉'")

    # 社会经济指标
    education = Column(String(128), comment="最高学历，示例: '硕士(985)' 或 '本科(双非)'")
    occupation = Column(String(128), comment="职业行业，示例: '互联网-算法工程师' 或 '医疗-内科医生'")
    income_level = Column(String(128), comment="年薪范围，示例: '30w-50w' 或 '20k/月'")

    # 生活习惯
    smoking_drinking = Column(String(128), comment="烟酒偏好，示例: '不抽烟不喝酒' 或 '社交性饮酒，不吸烟'")


class FriendHardware(Base):
    __tablename__ = "friend_hardware"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")
    # 基础数值指标
    birth_year = Column(Integer, comment="出生年份，示例: 1998")
    height = Column(Integer, comment="身高(cm)，示例: 175")

    # 地域与背景
    city = Column(String(128), comment="常住城市，示例: '上海市' 或 '杭州市'")
    hometown = Column(String(128), comment="籍贯背景，示例: '山东青岛' 或 '新疆昌吉'")

    # 社会经济指标
    education = Column(String(128), comment="最高学历，示例: '硕士(985)' 或 '本科(双非)'")
    occupation = Column(String(128), comment="职业行业，示例: '互联网-算法工程师' 或 '医疗-内科医生'")
    income_level = Column(String(128), comment="年薪范围，示例: '30w-50w' 或 '20k/月'")

    # 生活习惯
    smoking_drinking = Column(String(128), comment="烟酒偏好，示例: '不抽烟不喝酒' 或 '社交性饮酒，不吸烟'")
