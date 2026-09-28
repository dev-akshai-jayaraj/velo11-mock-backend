import uuid
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class SeasonBase(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool = False
    status: str = "ACTIVE"


class SeasonCreate(SeasonBase):
    pass


class SeasonUpdate(BaseModel):
    name: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_active: bool | None = None
    status: str | None = None


class SeasonRead(SeasonBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CompetitionBase(BaseModel):
    name: str
    type: str | None = None
    country: str | None = None
    level: str | None = None
    status: str = "ACTIVE"


class CompetitionCreate(CompetitionBase):
    pass


class CompetitionUpdate(BaseModel):
    name: str | None = None
    type: str | None = None
    country: str | None = None
    level: str | None = None
    status: str | None = None


class CompetitionRead(CompetitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PlayerPositionBase(BaseModel):
    name: str
    code: str
    position_group: str | None = None
    display_order: int | None = None
    status: str = "ACTIVE"


class PlayerPositionCreate(PlayerPositionBase):
    pass


class PlayerPositionUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    position_group: str | None = None
    display_order: int | None = None
    status: str | None = None


class PlayerPositionRead(PlayerPositionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class CompetitionSeasonBase(BaseModel):
    competition_id: uuid.UUID
    season_id: uuid.UUID
    status: str = "ACTIVE"


class CompetitionSeasonCreate(CompetitionSeasonBase):
    pass


class CompetitionSeasonUpdate(BaseModel):
    competition_id: uuid.UUID | None = None
    season_id: uuid.UUID | None = None
    status: str | None = None


class CompetitionSeasonRead(CompetitionSeasonBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TeamCompetitionBase(BaseModel):
    own_team_id: uuid.UUID
    competition_season_id: uuid.UUID
    is_primary: bool = False
    status: str = "ACTIVE"


class TeamCompetitionCreate(TeamCompetitionBase):
    pass


class TeamCompetitionUpdate(BaseModel):
    own_team_id: uuid.UUID | None = None
    competition_season_id: uuid.UUID | None = None
    is_primary: bool | None = None
    status: str | None = None


class TeamCompetitionRead(TeamCompetitionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
