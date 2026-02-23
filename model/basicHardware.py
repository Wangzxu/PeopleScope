from sqlalchemy import Column, Integer, String
from core.db.mysql import Base


class BasicHardware(Base):
    __tablename__ = "hardware"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="主键ID")
    user = Column(String(64), nullable=False, comment="用户名")
    birth_year = Column(Integer, comment="出生年份，如1998")
    height = Column(Integer, comment="身高，单位cm")
    city = Column(String(128), comment="目前常住的城市")
    education = Column(String(128), comment="最高学历")
    occupation = Column(String(128), comment="职业或所在行业")
    income_level = Column(String(128), comment="大致的年薪范围")
    smoking_drinking = Column(String(128), comment="烟酒偏好描述")
    hometown = Column(String(128), comment="籍贯或家乡背景")
