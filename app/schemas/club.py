import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HomeClubBase(BaseModel):
    name: str
    short_name: str | None = None
    logo_url: str | None = None
    country: str | None = None
    timezone: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    home_venue_id: uuid.UUID | None = None
    status: str = "ACTIVE"


class HomeClubCreate(HomeClubBase):
    pass


class HomeClubUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    logo_url: str | None = None
    country: str | None = None
    timezone: str | None = None
    primary_color: str | None = None
    secondary_color: str | None = None
    home_venue_id: uuid.UUID | None = None
    status: str | None = None


class HomeClubRead(HomeClubBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class VenueBase(BaseModel):
    name: str
    country: str | None = None
    city: str | None = None
    address: str | None = None
    surface_type: str | None = None
    capacity: int | None = None
    is_home_venue: bool = False
    status: str = "ACTIVE"


class VenueCreate(VenueBase):
    pass


class VenueUpdate(BaseModel):
    name: str | None = None
    country: str | None = None
    city: str | None = None
    address: str | None = None
    surface_type: str | None = None
    capacity: int | None = None
    is_home_venue: bool | None = None
    status: str | None = None


class VenueRead(VenueBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OwnTeamBase(BaseModel):
    home_club_id: uuid.UUID
    name: str
    short_name: str | None = None
    team_type: str | None = None
    gender: str | None = None
    age_group: str | None = None
    status: str = "ACTIVE"


class OwnTeamCreate(OwnTeamBase):
    pass


class OwnTeamUpdate(BaseModel):
    home_club_id: uuid.UUID | None = None
    name: str | None = None
    short_name: str | None = None
    team_type: str | None = None
    gender: str | None = None
    age_group: str | None = None
    status: str | None = None


class OwnTeamRead(OwnTeamBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
