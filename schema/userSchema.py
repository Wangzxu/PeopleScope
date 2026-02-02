from pydantic import BaseModel, ConfigDict
from typing import Dict, List, Optional


class UserRes(BaseModel):
    id: int
    user: str
    tags: Optional[Dict[str, List[str]]] = None
    model_config = ConfigDict(from_attributes=True)


class UserRequest(BaseModel):
    user: str
