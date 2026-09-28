import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import DataSourceType, JSONValue


class DataSourceBase(BaseModel):
    name: str
    source_type: DataSourceType
    provider: str | None = None
    base_url: str | None = None
    is_active: bool = True
    configuration: JSONValue | None = None


class DataSourceCreate(DataSourceBase):
    pass


class DataSourceUpdate(BaseModel):
    name: str | None = None
    source_type: DataSourceType | None = None
    provider: str | None = None
    base_url: str | None = None
    is_active: bool | None = None
    configuration: JSONValue | None = None


class DataSourceRead(DataSourceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class DataImportBase(BaseModel):
    data_source_id: uuid.UUID
    home_club_id: uuid.UUID | None = None
    import_type: str
    file_name: str | None = None
    external_reference: str | None = None
    status: str = "PENDING"
    records_received: int = Field(0, ge=0)
    records_processed: int = Field(0, ge=0)
    records_failed: int = Field(0, ge=0)
    error_details: JSONValue | None = None
    imported_by: uuid.UUID | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class DataImportCreate(DataImportBase):
    @model_validator(mode="after")
    def _check_counts(self):
        if self.records_processed + self.records_failed > self.records_received:
            raise ValueError("records_processed + records_failed cannot exceed records_received")
        if self.started_at and self.completed_at and self.completed_at < self.started_at:
            raise ValueError("completed_at cannot be before started_at")
        return self


class DataImportUpdate(BaseModel):
    status: str | None = None
    file_name: str | None = None
    external_reference: str | None = None
    records_received: int | None = Field(None, ge=0)
    records_processed: int | None = Field(None, ge=0)
    records_failed: int | None = Field(None, ge=0)
    error_details: JSONValue | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class DataImportRead(DataImportBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
