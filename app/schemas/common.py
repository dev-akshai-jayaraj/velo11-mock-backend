from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ErrorDetail(BaseModel):
    code: str
    message: str


class APIResponse(BaseModel, Generic[T]):
    status: bool
    message: str
    result: T | None = None
    error: ErrorDetail | None = None

    @classmethod
    def ok(cls, *, message: str, result: T | None = None) -> "APIResponse[T]":
        return cls(status=True, message=message, result=result, error=None)

    @classmethod
    def fail(cls, *, message: str, code: str) -> "APIResponse[T]":
        return cls(status=False, message=message, result=None, error=ErrorDetail(code=code, message=message))
