import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.common import JSONValue


class AnalyticsSnapshotBase(BaseModel):
    home_club_id: uuid.UUID
    own_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    analytics_type: str
    scope_type: str
    title: str | None = None
    metrics: JSONValue
    explanation: str | None = None
    model_version: str | None = None
    calculated_at: datetime


class AnalyticsSnapshotCreate(AnalyticsSnapshotBase):
    pass


class AnalyticsSnapshotRead(AnalyticsSnapshotBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime


class RecommendationBase(BaseModel):
    home_club_id: uuid.UUID
    own_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    recommendation_type: str
    title: str
    recommendation: str
    rationale: str | None = None
    priority: str | None = None
    confidence: float | None = Field(None, ge=0, le=1)
    status: str = "OPEN"
    generated_by: str = "MANUAL"
    created_by: uuid.UUID | None = None


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    own_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    recommendation_type: str | None = None
    title: str | None = None
    recommendation: str | None = None
    rationale: str | None = None
    priority: str | None = None
    confidence: float | None = Field(None, ge=0, le=1)
    status: str | None = None


class RecommendationRead(RecommendationBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReportBase(BaseModel):
    home_club_id: uuid.UUID
    own_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    report_type: str
    title: str
    content: JSONValue
    status: str = "DRAFT"
    created_by: uuid.UUID


class ReportCreate(ReportBase):
    pass


class ReportUpdate(BaseModel):
    own_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    report_type: str | None = None
    title: str | None = None
    content: JSONValue | None = None
    status: str | None = None
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None


class ReportRead(ReportBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    approved_by: uuid.UUID | None = None
    approved_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
