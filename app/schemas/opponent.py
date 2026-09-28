import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OpponentClubBase(BaseModel):
    name: str
    short_name: str | None = None
    logo_url: str | None = None
    country: str | None = None
    city: str | None = None
    status: str = "ACTIVE"


class OpponentClubCreate(OpponentClubBase):
    pass


class OpponentClubUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    logo_url: str | None = None
    country: str | None = None
    city: str | None = None
    status: str | None = None


class OpponentClubRead(OpponentClubBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OpponentTeamBase(BaseModel):
    opponent_club_id: uuid.UUID
    name: str
    short_name: str | None = None
    team_type: str | None = None
    gender: str | None = None
    age_group: str | None = None
    status: str = "ACTIVE"


class OpponentTeamCreate(OpponentTeamBase):
    pass


class OpponentTeamUpdate(BaseModel):
    opponent_club_id: uuid.UUID | None = None
    name: str | None = None
    short_name: str | None = None
    team_type: str | None = None
    gender: str | None = None
    age_group: str | None = None
    status: str | None = None


class OpponentTeamRead(OpponentTeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
