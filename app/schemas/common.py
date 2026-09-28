from datetime import date
from typing import Any, Generic, Literal, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

# jsonb columns: the ERD uses them for both objects (e.g. metrics) and lists (e.g. tags).
JSONValue = dict[str, Any] | list[Any]

# Enumerations the ERD spells out explicitly; other status/type columns stay free text.
TeamScope = Literal["OWN", "OPPONENT"]
VenueSide = Literal["HOME", "AWAY", "NEUTRAL"]
MatchResult = Literal["WIN", "DRAW", "LOSS"]
SetPiecePhase = Literal["ATTACKING", "DEFENDING"]
DataSourceType = Literal["MANUAL", "CSV", "EXCEL", "API", "SCRAPER"]


def ensure_not_before(earlier: date | None, later: date | None, *, earlier_name: str, later_name: str) -> None:
    if earlier is not None and later is not None and later < earlier:
        raise ValueError(f"{later_name} cannot be before {earlier_name}")


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
