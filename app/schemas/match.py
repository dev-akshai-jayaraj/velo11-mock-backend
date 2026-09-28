import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.schemas.common import JSONValue, MatchResult, TeamScope, VenueSide


class FixtureBase(BaseModel):
    own_team_id: uuid.UUID
    opponent_team_id: uuid.UUID
    competition_season_id: uuid.UUID | None = None
    venue_id: uuid.UUID | None = None
    scheduled_at: datetime
    venue_side: VenueSide
    round_name: str | None = None
    matchweek: int | None = Field(None, ge=1)
    status: str = "SCHEDULED"
    source_type: str = "MANUAL"
    external_reference: str | None = None


class FixtureCreate(FixtureBase):
    pass


class FixtureUpdate(BaseModel):
    own_team_id: uuid.UUID | None = None
    opponent_team_id: uuid.UUID | None = None
    competition_season_id: uuid.UUID | None = None
    venue_id: uuid.UUID | None = None
    scheduled_at: datetime | None = None
    venue_side: VenueSide | None = None
    round_name: str | None = None
    matchweek: int | None = Field(None, ge=1)
    status: str | None = None
    source_type: str | None = None
    external_reference: str | None = None


class FixtureRead(FixtureBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


def _result_from_score(own: int, opponent: int) -> str:
    if own > opponent:
        return "WIN"
    if own < opponent:
        return "LOSS"
    return "DRAW"


class MatchBase(BaseModel):
    fixture_id: uuid.UUID
    own_score: int | None = Field(None, ge=0)
    opponent_score: int | None = Field(None, ge=0)
    halftime_own_score: int | None = Field(None, ge=0)
    halftime_opponent_score: int | None = Field(None, ge=0)
    result: MatchResult | None = None
    analysis_status: str = "PRE_MATCH"
    kickoff_at: datetime | None = None
    finished_at: datetime | None = None
    notes: str | None = None


class MatchCreate(MatchBase):
    @model_validator(mode="after")
    def _derive_result(self):
        # When both final scores are known the result is implied by them: fill it in
        # if omitted, and reject a contradictory one rather than store bad data.
        if self.own_score is not None and self.opponent_score is not None:
            expected = _result_from_score(self.own_score, self.opponent_score)
            if self.result is None:
                self.result = expected
            elif self.result != expected:
                raise ValueError(
                    f"result '{self.result}' contradicts score {self.own_score}-{self.opponent_score}"
                )
        if self.kickoff_at and self.finished_at and self.finished_at < self.kickoff_at:
            raise ValueError("finished_at cannot be before kickoff_at")
        return self


class MatchUpdate(BaseModel):
    own_score: int | None = Field(None, ge=0)
    opponent_score: int | None = Field(None, ge=0)
    halftime_own_score: int | None = Field(None, ge=0)
    halftime_opponent_score: int | None = Field(None, ge=0)
    result: MatchResult | None = None
    analysis_status: str | None = None
    kickoff_at: datetime | None = None
    finished_at: datetime | None = None
    notes: str | None = None

    @model_validator(mode="after")
    def _derive_result(self):
        if self.own_score is not None and self.opponent_score is not None:
            expected = _result_from_score(self.own_score, self.opponent_score)
            if self.result is None:
                self.result = expected
            elif self.result != expected:
                raise ValueError(
                    f"result '{self.result}' contradicts score {self.own_score}-{self.opponent_score}"
                )
        return self


class MatchRead(MatchBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MatchContextBase(BaseModel):
    match_id: uuid.UUID
    importance: str | None = None
    competition_context: str | None = None
    schedule_context: str | None = None
    travel_context: str | None = None
    weather_context: str | None = None
    pitch_context: str | None = None
    expected_conditions: JSONValue | None = None
    analyst_notes: str | None = None


class MatchContextCreate(MatchContextBase):
    pass


class MatchContextUpdate(BaseModel):
    importance: str | None = None
    competition_context: str | None = None
    schedule_context: str | None = None
    travel_context: str | None = None
    weather_context: str | None = None
    pitch_context: str | None = None
    expected_conditions: JSONValue | None = None
    analyst_notes: str | None = None


class MatchContextRead(MatchContextBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MatchLineupBase(BaseModel):
    match_id: uuid.UUID
    team_scope: TeamScope
    formation: str | None = None
    lineup_type: str = "STARTING"
    confirmed_at: datetime | None = None


class MatchLineupCreate(MatchLineupBase):
    pass


class MatchLineupUpdate(BaseModel):
    match_id: uuid.UUID | None = None
    team_scope: TeamScope | None = None
    formation: str | None = None
    lineup_type: str | None = None
    confirmed_at: datetime | None = None


class MatchLineupRead(MatchLineupBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MatchLineupPlayerBase(BaseModel):
    lineup_id: uuid.UUID
    # Own-squad entries reference players; opposition entries only carry a name,
    # since opposition players are not modelled as player records.
    player_id: uuid.UUID | None = None
    opponent_player_name: str | None = None
    position_id: uuid.UUID | None = None
    shirt_number: int | None = Field(None, ge=0)
    is_starter: bool = True
    minute_on: int | None = Field(None, ge=0)
    minute_off: int | None = Field(None, ge=0)


class MatchLineupPlayerCreate(MatchLineupPlayerBase):
    @model_validator(mode="after")
    def _check_identity_and_minutes(self):
        if self.player_id is None and not self.opponent_player_name:
            raise ValueError("either player_id or opponent_player_name is required")
        if self.player_id is not None and self.opponent_player_name:
            raise ValueError("provide player_id or opponent_player_name, not both")
        if self.minute_on is not None and self.minute_off is not None and self.minute_off < self.minute_on:
            raise ValueError("minute_off cannot be before minute_on")
        return self


class MatchLineupPlayerUpdate(BaseModel):
    lineup_id: uuid.UUID | None = None
    player_id: uuid.UUID | None = None
    opponent_player_name: str | None = None
    position_id: uuid.UUID | None = None
    shirt_number: int | None = Field(None, ge=0)
    is_starter: bool | None = None
    minute_on: int | None = Field(None, ge=0)
    minute_off: int | None = Field(None, ge=0)


class MatchLineupPlayerRead(MatchLineupPlayerBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class MatchEventBase(BaseModel):
    match_id: uuid.UUID
    team_scope: TeamScope
    player_id: uuid.UUID | None = None
    event_type: str
    minute: int | None = Field(None, ge=0)
    second: int | None = Field(None, ge=0, le=59)
    period: str | None = None
    x: float | None = None
    y: float | None = None
    outcome: str | None = None
    details: JSONValue | None = None
    source_type: str = "MANUAL"


class MatchEventCreate(MatchEventBase):
    @model_validator(mode="after")
    def _check_player_scope(self):
        if self.team_scope == "OPPONENT" and self.player_id is not None:
            raise ValueError("player_id can only be set on OWN events (opposition players are not player records)")
        return self


class MatchEventUpdate(BaseModel):
    team_scope: TeamScope | None = None
    player_id: uuid.UUID | None = None
    event_type: str | None = None
    minute: int | None = Field(None, ge=0)
    second: int | None = Field(None, ge=0, le=59)
    period: str | None = None
    x: float | None = None
    y: float | None = None
    outcome: str | None = None
    details: JSONValue | None = None
    source_type: str | None = None


class MatchEventRead(MatchEventBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
