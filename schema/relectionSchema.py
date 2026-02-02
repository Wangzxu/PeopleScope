
from pydantic import BaseModel, Field


class Reflection(BaseModel):
    user: str = Field(..., description="用户ID")
    question: str = Field(..., description="问题内容")
    question_id: int = Field(..., description="问题id")
    answer: str = Field(..., description="用户回答")
