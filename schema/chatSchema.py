from pydantic import BaseModel, ConfigDict
from datetime import datetime


class ChatRes(BaseModel):
    id: int
    session_id: int
    type: int
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatListRes(BaseModel):
    session_id: int
    chats: list[ChatRes]

class ChatRequest(BaseModel):
    user: str
    message: str
    session_id: int
    