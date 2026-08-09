import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AuditLogBase(BaseModel):
    module_code: str
    record_id: uuid.UUID
    action: str
    changed_by: uuid.UUID | None = None
    old_value: dict[str, Any] | None = None
    new_value: dict[str, Any] | None = None
    source_type: str = "MANUAL"
    changed_at: datetime


class AuditLogCreate(AuditLogBase):
    pass


class AuditLogRead(AuditLogBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
