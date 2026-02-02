from dataclasses import dataclass
from pydantic import BaseModel, ConfigDict
from datetime import datetime


from typing import Optional

class SessionRes(BaseModel):
    id: int
    user: str
    title: str
    content: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SessionRequest(BaseModel):
    user: str
    message: Optional[str] = None


class SessionRenameRequest(BaseModel):
    session_id: int
    title: str


class SessionDeleteRequest(BaseModel):
    session_id: int
