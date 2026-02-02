from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class Result(BaseModel, Generic[T]):
    code: int
    message: str
    data: Optional[T] = None

    @staticmethod
    def success(data: T = None, message: str = "success"):
        return Result(code=0, message=message, data=data)

    @staticmethod
    def fail(message: str = "fail", code: int = -1):
        return Result(code=code, message=message, data=None)
