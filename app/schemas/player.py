import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import ensure_not_before


class PlayerBase(BaseModel):
    first_name: str
    last_name: str | None = None
    display_name: str
    date_of_birth: date | None = None
    nationality: str | None = None
    preferred_foot: str | None = None
    height_cm: int | None = Field(None, gt=0)
    weight_kg: float | None = Field(None, gt=0)
    primary_position_id: uuid.UUID | None = None
    photo_url: str | None = None
    external_reference: str | None = None
    status: str = "ACTIVE"


class PlayerCreate(PlayerBase):
    pass


class PlayerUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    display_name: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = None
    preferred_foot: str | None = None
    height_cm: int | None = Field(None, gt=0)
    weight_kg: float | None = Field(None, gt=0)
    primary_position_id: uuid.UUID | None = None
    photo_url: str | None = None
    external_reference: str | None = None
    status: str | None = None


class PlayerRead(PlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TeamPlayerBase(BaseModel):
    own_team_id: uuid.UUID
    player_id: uuid.UUID
    season_id: uuid.UUID
    squad_number: int | None = Field(None, ge=0)
    position_id: uuid.UUID | None = None
    joined_at: date | None = None
    left_at: date | None = None
    is_captain: bool = False
    status: str = "ACTIVE"


class TeamPlayerCreate(TeamPlayerBase):
    @model_validator(mode="after")
    def _check_dates(self):
        ensure_not_before(self.joined_at, self.left_at, earlier_name="joined_at", later_name="left_at")
        return self


class TeamPlayerUpdate(BaseModel):
    own_team_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    season_id: uuid.UUID | None = None
    squad_number: int | None = Field(None, ge=0)
    position_id: uuid.UUID | None = None
    joined_at: date | None = None
    left_at: date | None = None
    is_captain: bool | None = None
    status: str | None = None


class TeamPlayerRead(TeamPlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PlayerAvailabilityBase(BaseModel):
    player_id: uuid.UUID
    own_team_id: uuid.UUID
    availability_status: str
    reason_type: str | None = None
    reason: str | None = None
    start_date: date
    expected_return_date: date | None = None
    actual_return_date: date | None = None
    medical_notes: str | None = None


class PlayerAvailabilityCreate(PlayerAvailabilityBase):
    @model_validator(mode="after")
    def _check_dates(self):
        ensure_not_before(
            self.start_date, self.expected_return_date,
            earlier_name="start_date", later_name="expected_return_date",
        )
        ensure_not_before(
            self.start_date, self.actual_return_date,
            earlier_name="start_date", later_name="actual_return_date",
        )
        return self


class PlayerAvailabilityUpdate(BaseModel):
    player_id: uuid.UUID | None = None
    own_team_id: uuid.UUID | None = None
    availability_status: str | None = None
    reason_type: str | None = None
    reason: str | None = None
    start_date: date | None = None
    expected_return_date: date | None = None
    actual_return_date: date | None = None
    medical_notes: str | None = None


class PlayerAvailabilityRead(PlayerAvailabilityBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
