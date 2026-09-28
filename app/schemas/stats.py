import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import JSONValue, TeamScope


def _check_not_greater(values: dict, pairs: list[tuple[str, str]]) -> None:
    for part, whole in pairs:
        if values.get(part) is not None and values.get(whole) is not None and values[part] > values[whole]:
            raise ValueError(f"{part} cannot exceed {whole}")


class PlayerMatchStatBase(BaseModel):
    match_id: uuid.UUID
    player_id: uuid.UUID
    own_team_id: uuid.UUID
    minutes_played: int = Field(0, ge=0)
    started: bool = False
    goals: int = Field(0, ge=0)
    assists: int = Field(0, ge=0)
    shots: int = Field(0, ge=0)
    shots_on_target: int = Field(0, ge=0)
    passes_attempted: int = Field(0, ge=0)
    passes_completed: int = Field(0, ge=0)
    tackles: int = Field(0, ge=0)
    interceptions: int = Field(0, ge=0)
    clearances: int = Field(0, ge=0)
    touches: int = Field(0, ge=0)
    yellow_cards: int = Field(0, ge=0)
    red_cards: int = Field(0, ge=0)
    xg: float | None = Field(None, ge=0)
    xa: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None


class PlayerMatchStatCreate(PlayerMatchStatBase):
    @model_validator(mode="after")
    def _check_totals(self):
        _check_not_greater(
            self.model_dump(),
            [("shots_on_target", "shots"), ("passes_completed", "passes_attempted")],
        )
        return self


class PlayerMatchStatUpdate(BaseModel):
    own_team_id: uuid.UUID | None = None
    minutes_played: int | None = Field(None, ge=0)
    started: bool | None = None
    goals: int | None = Field(None, ge=0)
    assists: int | None = Field(None, ge=0)
    shots: int | None = Field(None, ge=0)
    shots_on_target: int | None = Field(None, ge=0)
    passes_attempted: int | None = Field(None, ge=0)
    passes_completed: int | None = Field(None, ge=0)
    tackles: int | None = Field(None, ge=0)
    interceptions: int | None = Field(None, ge=0)
    clearances: int | None = Field(None, ge=0)
    touches: int | None = Field(None, ge=0)
    yellow_cards: int | None = Field(None, ge=0)
    red_cards: int | None = Field(None, ge=0)
    xg: float | None = Field(None, ge=0)
    xa: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None


class PlayerMatchStatRead(PlayerMatchStatBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TeamMatchStatBase(BaseModel):
    match_id: uuid.UUID
    team_scope: TeamScope
    possession_pct: float | None = Field(None, ge=0, le=100)
    shots: int | None = Field(None, ge=0)
    shots_on_target: int | None = Field(None, ge=0)
    passes_attempted: int | None = Field(None, ge=0)
    passes_completed: int | None = Field(None, ge=0)
    pass_completion_pct: float | None = Field(None, ge=0, le=100)
    corners: int | None = Field(None, ge=0)
    fouls: int | None = Field(None, ge=0)
    offsides: int | None = Field(None, ge=0)
    yellow_cards: int | None = Field(None, ge=0)
    red_cards: int | None = Field(None, ge=0)
    xg: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None


class TeamMatchStatCreate(TeamMatchStatBase):
    @model_validator(mode="after")
    def _check_totals(self):
        _check_not_greater(
            self.model_dump(),
            [("shots_on_target", "shots"), ("passes_completed", "passes_attempted")],
        )
        return self


class TeamMatchStatUpdate(BaseModel):
    possession_pct: float | None = Field(None, ge=0, le=100)
    shots: int | None = Field(None, ge=0)
    shots_on_target: int | None = Field(None, ge=0)
    passes_attempted: int | None = Field(None, ge=0)
    passes_completed: int | None = Field(None, ge=0)
    pass_completion_pct: float | None = Field(None, ge=0, le=100)
    corners: int | None = Field(None, ge=0)
    fouls: int | None = Field(None, ge=0)
    offsides: int | None = Field(None, ge=0)
    yellow_cards: int | None = Field(None, ge=0)
    red_cards: int | None = Field(None, ge=0)
    xg: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None


class TeamMatchStatRead(TeamMatchStatBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PlayerSeasonStatBase(BaseModel):
    player_id: uuid.UUID
    own_team_id: uuid.UUID
    season_id: uuid.UUID
    competition_id: uuid.UUID | None = None
    appearances: int = Field(0, ge=0)
    starts: int = Field(0, ge=0)
    minutes_played: int = Field(0, ge=0)
    goals: int = Field(0, ge=0)
    assists: int = Field(0, ge=0)
    xg: float | None = Field(None, ge=0)
    xa: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None
    calculated_at: datetime | None = None


class PlayerSeasonStatCreate(PlayerSeasonStatBase):
    @model_validator(mode="after")
    def _check_totals(self):
        _check_not_greater(self.model_dump(), [("starts", "appearances")])
        return self


class PlayerSeasonStatUpdate(BaseModel):
    appearances: int | None = Field(None, ge=0)
    starts: int | None = Field(None, ge=0)
    minutes_played: int | None = Field(None, ge=0)
    goals: int | None = Field(None, ge=0)
    assists: int | None = Field(None, ge=0)
    xg: float | None = Field(None, ge=0)
    xa: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None
    calculated_at: datetime | None = None


class PlayerSeasonStatRead(PlayerSeasonStatBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TeamSeasonStatBase(BaseModel):
    own_team_id: uuid.UUID
    season_id: uuid.UUID
    competition_id: uuid.UUID | None = None
    matches_played: int = Field(0, ge=0)
    wins: int = Field(0, ge=0)
    draws: int = Field(0, ge=0)
    losses: int = Field(0, ge=0)
    goals_for: int = Field(0, ge=0)
    goals_against: int = Field(0, ge=0)
    xg_for: float | None = Field(None, ge=0)
    xg_against: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None
    calculated_at: datetime | None = None


class TeamSeasonStatCreate(TeamSeasonStatBase):
    @model_validator(mode="after")
    def _check_record(self):
        if self.wins + self.draws + self.losses > self.matches_played:
            raise ValueError("wins + draws + losses cannot exceed matches_played")
        return self


class TeamSeasonStatUpdate(BaseModel):
    matches_played: int | None = Field(None, ge=0)
    wins: int | None = Field(None, ge=0)
    draws: int | None = Field(None, ge=0)
    losses: int | None = Field(None, ge=0)
    goals_for: int | None = Field(None, ge=0)
    goals_against: int | None = Field(None, ge=0)
    xg_for: float | None = Field(None, ge=0)
    xg_against: float | None = Field(None, ge=0)
    extended_stats: JSONValue | None = None
    calculated_at: datetime | None = None


class TeamSeasonStatRead(TeamSeasonStatBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
