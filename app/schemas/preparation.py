import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, model_validator

from app.schemas.common import JSONValue, SetPiecePhase


class ScoutingNoteBase(BaseModel):
    player_id: uuid.UUID | None = None
    opponent_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    author_id: uuid.UUID
    note_type: str | None = None
    title: str | None = None
    notes: str
    tags: JSONValue | None = None
    visibility: str = "INTERNAL"


class ScoutingNoteCreate(ScoutingNoteBase):
    @model_validator(mode="after")
    def _check_subject(self):
        if self.player_id is None and self.opponent_team_id is None and self.match_id is None:
            raise ValueError("a scouting note must be about a player, an opponent team or a match")
        return self


class ScoutingNoteUpdate(BaseModel):
    player_id: uuid.UUID | None = None
    opponent_team_id: uuid.UUID | None = None
    match_id: uuid.UUID | None = None
    note_type: str | None = None
    title: str | None = None
    notes: str | None = None
    tags: JSONValue | None = None
    visibility: str | None = None


class ScoutingNoteRead(ScoutingNoteBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class OppositionAnalysisBase(BaseModel):
    match_id: uuid.UUID
    opponent_team_id: uuid.UUID
    analyst_id: uuid.UUID | None = None
    summary: str | None = None
    strengths: JSONValue | None = None
    weaknesses: JSONValue | None = None
    attacking_patterns: JSONValue | None = None
    defensive_patterns: JSONValue | None = None
    transition_patterns: JSONValue | None = None
    key_players: JSONValue | None = None
    threats: JSONValue | None = None
    opportunities: JSONValue | None = None


class OppositionAnalysisCreate(OppositionAnalysisBase):
    pass


class OppositionAnalysisUpdate(BaseModel):
    analyst_id: uuid.UUID | None = None
    summary: str | None = None
    strengths: JSONValue | None = None
    weaknesses: JSONValue | None = None
    attacking_patterns: JSONValue | None = None
    defensive_patterns: JSONValue | None = None
    transition_patterns: JSONValue | None = None
    key_players: JSONValue | None = None
    threats: JSONValue | None = None
    opportunities: JSONValue | None = None


class OppositionAnalysisRead(OppositionAnalysisBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TacticalPlanBase(BaseModel):
    match_id: uuid.UUID
    own_team_id: uuid.UUID
    created_by: uuid.UUID | None = None
    formation: str | None = None
    game_model: str | None = None
    in_possession_plan: str | None = None
    out_of_possession_plan: str | None = None
    transition_plan: str | None = None
    pressing_plan: str | None = None
    notes: str | None = None
    status: str = "DRAFT"


class TacticalPlanCreate(TacticalPlanBase):
    pass


class TacticalPlanUpdate(BaseModel):
    formation: str | None = None
    game_model: str | None = None
    in_possession_plan: str | None = None
    out_of_possession_plan: str | None = None
    transition_plan: str | None = None
    pressing_plan: str | None = None
    notes: str | None = None
    status: str | None = None


class TacticalPlanRead(TacticalPlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class SetPiecePlanBase(BaseModel):
    match_id: uuid.UUID
    own_team_id: uuid.UUID
    phase: SetPiecePhase
    set_piece_type: str
    title: str | None = None
    instructions: str | None = None
    assignments: JSONValue | None = None
    created_by: uuid.UUID | None = None


class SetPiecePlanCreate(SetPiecePlanBase):
    pass


class SetPiecePlanUpdate(BaseModel):
    phase: SetPiecePhase | None = None
    set_piece_type: str | None = None
    title: str | None = None
    instructions: str | None = None
    assignments: JSONValue | None = None


class SetPiecePlanRead(SetPiecePlanBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
