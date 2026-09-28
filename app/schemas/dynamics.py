import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import JSONValue


class TeamDynamicsAssessmentBase(BaseModel):
    own_team_id: uuid.UUID
    season_id: uuid.UUID | None = None
    assessed_at: datetime
    assessed_by: uuid.UUID | None = None
    cohesion_score: float | None = None
    chemistry_score: float | None = None
    leadership_score: float | None = None
    morale_score: float | None = None
    notes: str | None = None
    evidence: JSONValue | None = None


class TeamDynamicsAssessmentCreate(TeamDynamicsAssessmentBase):
    pass


class TeamDynamicsAssessmentUpdate(BaseModel):
    season_id: uuid.UUID | None = None
    assessed_at: datetime | None = None
    assessed_by: uuid.UUID | None = None
    cohesion_score: float | None = None
    chemistry_score: float | None = None
    leadership_score: float | None = None
    morale_score: float | None = None
    notes: str | None = None
    evidence: JSONValue | None = None


class TeamDynamicsAssessmentRead(TeamDynamicsAssessmentBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PlayerRelationshipBase(BaseModel):
    own_team_id: uuid.UUID
    player_a_id: uuid.UUID
    player_b_id: uuid.UUID
    relationship_type: str | None = None
    score: float | None = None
    sample_size: int | None = Field(None, ge=0)
    evidence: JSONValue | None = None
    calculated_at: datetime | None = None


class PlayerRelationshipCreate(PlayerRelationshipBase):
    @model_validator(mode="after")
    def _check_distinct_players(self):
        if self.player_a_id == self.player_b_id:
            raise ValueError("player_a_id and player_b_id must be different players")
        return self


class PlayerRelationshipUpdate(BaseModel):
    relationship_type: str | None = None
    score: float | None = None
    sample_size: int | None = Field(None, ge=0)
    evidence: JSONValue | None = None
    calculated_at: datetime | None = None


class PlayerRelationshipRead(PlayerRelationshipBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UnitCohesionBase(BaseModel):
    own_team_id: uuid.UUID
    season_id: uuid.UUID | None = None
    unit_type: str
    unit_name: str | None = None
    score: float | None = None
    evidence: JSONValue | None = None
    calculated_at: datetime | None = None


class UnitCohesionCreate(UnitCohesionBase):
    pass


class UnitCohesionUpdate(BaseModel):
    season_id: uuid.UUID | None = None
    unit_type: str | None = None
    unit_name: str | None = None
    score: float | None = None
    evidence: JSONValue | None = None
    calculated_at: datetime | None = None


class UnitCohesionRead(UnitCohesionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
