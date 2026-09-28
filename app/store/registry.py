"""Single source of truth for the CSV-backed data model.

Mirrors the tables in db/football_intelligence_expanded.dbml. Both the runtime CsvRepository and the
scripts/generate_mock_data.py generator read this registry, so the on-disk
CSV shape and the mock data can never drift from each other.
"""

from dataclasses import dataclass, field
from enum import Enum


class FieldType(str, Enum):
    STR = "str"
    INT = "int"
    FLOAT = "float"  # Postgres numeric
    BOOL = "bool"
    UUID = "uuid"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"


@dataclass(frozen=True)
class FieldSpec:
    name: str
    type: FieldType
    fk: str | None = None  # entity name this field references, if any
    auto_now_add: bool = False  # set to "now" on create if the caller didn't supply it
    auto_now: bool = False  # set to "now" on every create AND update (implies auto_now_add)


@dataclass(frozen=True)
class EntitySpec:
    name: str
    csv_file: str
    fields: list[FieldSpec]
    unique: list[tuple[str, ...]] = field(default_factory=list)

    @property
    def fieldnames(self) -> list[str]:
        return [f.name for f in self.fields]

    @property
    def fk_fields(self) -> list[FieldSpec]:
        return [f for f in self.fields if f.fk]

    @property
    def auto_now_add_fields(self) -> list[str]:
        """Fields stamped with 'now' on create only, if the caller didn't supply a value."""
        return [f.name for f in self.fields if f.auto_now_add or f.auto_now]

    @property
    def auto_now_fields(self) -> list[str]:
        """Fields re-stamped with 'now' on every update."""
        return [f.name for f in self.fields if f.auto_now]


REGISTRY: dict[str, EntitySpec] = {}


def _register(spec: EntitySpec) -> EntitySpec:
    REGISTRY[spec.name] = spec
    return spec


F = FieldSpec
T = FieldType

HOME_CLUBS = _register(
    EntitySpec(
        name="home_clubs",
        csv_file="home_clubs.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("short_name", T.STR),
            F("logo_url", T.STR),
            F("country", T.STR),
            F("timezone", T.STR),
            F("primary_color", T.STR),
            F("secondary_color", T.STR),
            F("home_venue_id", T.UUID, fk="venues"),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

VENUES = _register(
    EntitySpec(
        name="venues",
        csv_file="venues.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("country", T.STR),
            F("city", T.STR),
            F("address", T.STR),
            F("surface_type", T.STR),
            F("capacity", T.INT),
            F("is_home_venue", T.BOOL),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

OWN_TEAMS = _register(
    EntitySpec(
        name="own_teams",
        csv_file="own_teams.csv",
        fields=[
            F("id", T.UUID),
            F("home_club_id", T.UUID, fk="home_clubs"),
            F("name", T.STR),
            F("short_name", T.STR),
            F("team_type", T.STR),
            F("gender", T.STR),
            F("age_group", T.STR),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

USERS = _register(
    EntitySpec(
        name="users",
        csv_file="users.csv",
        fields=[
            F("id", T.UUID),
            F("home_club_id", T.UUID, fk="home_clubs"),
            F("first_name", T.STR),
            F("last_name", T.STR),
            F("email", T.STR),
            F("password_hash", T.STR),
            F("phone", T.STR),
            F("status", T.STR),
            F("last_login_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("email",)],
    )
)

ROLES = _register(
    EntitySpec(
        name="roles",
        csv_file="roles.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("code", T.STR),
            F("description", T.STR),
            F("is_system_role", T.BOOL),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("code",)],
    )
)

PERMISSIONS = _register(
    EntitySpec(
        name="permissions",
        csv_file="permissions.csv",
        fields=[
            F("id", T.UUID),
            F("module_code", T.STR),
            F("action_code", T.STR),
            F("name", T.STR),
            F("description", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("module_code", "action_code")],
    )
)

USER_ROLES = _register(
    EntitySpec(
        name="user_roles",
        csv_file="user_roles.csv",
        fields=[
            F("id", T.UUID),
            F("user_id", T.UUID, fk="users"),
            F("role_id", T.UUID, fk="roles"),
            F("assigned_at", T.DATETIME, auto_now_add=True),
            F("assigned_by", T.UUID, fk="users"),
        ],
        unique=[("user_id", "role_id")],
    )
)

ROLE_PERMISSIONS = _register(
    EntitySpec(
        name="role_permissions",
        csv_file="role_permissions.csv",
        fields=[
            F("id", T.UUID),
            F("role_id", T.UUID, fk="roles"),
            F("permission_id", T.UUID, fk="permissions"),
            F("created_at", T.DATETIME, auto_now_add=True),
        ],
        unique=[("role_id", "permission_id")],
    )
)

SEASONS = _register(
    EntitySpec(
        name="seasons",
        csv_file="seasons.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("start_date", T.DATE),
            F("end_date", T.DATE),
            F("is_active", T.BOOL),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("name",)],
    )
)

COMPETITIONS = _register(
    EntitySpec(
        name="competitions",
        csv_file="competitions.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("type", T.STR),
            F("country", T.STR),
            F("level", T.STR),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

PLAYER_POSITIONS = _register(
    EntitySpec(
        name="player_positions",
        csv_file="player_positions.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("code", T.STR),
            F("position_group", T.STR),
            F("display_order", T.INT),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("code",)],
    )
)

SYSTEM_MODULES = _register(
    EntitySpec(
        name="system_modules",
        csv_file="system_modules.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("code", T.STR),
            F("description", T.STR),
            F("is_active", T.BOOL),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("code",)],
    )
)

APPROVAL_WORKFLOWS = _register(
    EntitySpec(
        name="approval_workflows",
        csv_file="approval_workflows.csv",
        fields=[
            F("id", T.UUID),
            F("module_id", T.UUID, fk="system_modules"),
            F("name", T.STR),
            F("code", T.STR),
            F("is_required", T.BOOL),
            F("is_active", T.BOOL),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("module_id", "code")],
    )
)

APPROVAL_STAGES = _register(
    EntitySpec(
        name="approval_stages",
        csv_file="approval_stages.csv",
        fields=[
            F("id", T.UUID),
            F("workflow_id", T.UUID, fk="approval_workflows"),
            F("name", T.STR),
            F("stage_order", T.INT),
            F("approval_type", T.STR),
            F("is_final_stage", T.BOOL),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("workflow_id", "stage_order")],
    )
)

APPROVAL_STAGE_APPROVERS = _register(
    EntitySpec(
        name="approval_stage_approvers",
        csv_file="approval_stage_approvers.csv",
        fields=[
            F("id", T.UUID),
            F("approval_stage_id", T.UUID, fk="approval_stages"),
            F("role_id", T.UUID, fk="roles"),
            F("user_id", T.UUID, fk="users"),
            F("approver_type", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

APPROVAL_REQUESTS = _register(
    EntitySpec(
        name="approval_requests",
        csv_file="approval_requests.csv",
        fields=[
            F("id", T.UUID),
            F("workflow_id", T.UUID, fk="approval_workflows"),
            F("module_id", T.UUID, fk="system_modules"),
            F("record_id", T.UUID),
            F("record_type", T.STR),
            F("current_status", T.STR),
            F("current_stage_order", T.INT),
            F("submitted_by", T.UUID, fk="users"),
            F("submitted_at", T.DATETIME),
            F("completed_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

APPROVAL_ACTIONS = _register(
    EntitySpec(
        name="approval_actions",
        csv_file="approval_actions.csv",
        fields=[
            F("id", T.UUID),
            F("approval_request_id", T.UUID, fk="approval_requests"),
            F("approval_stage_id", T.UUID, fk="approval_stages"),
            F("action_by", T.UUID, fk="users"),
            F("action", T.STR),
            F("comments", T.STR),
            F("action_at", T.DATETIME),
        ],
    )
)

AUDIT_LOGS = _register(
    EntitySpec(
        name="audit_logs",
        csv_file="audit_logs.csv",
        fields=[
            F("id", T.UUID),
            F("module_code", T.STR),
            F("record_id", T.UUID),
            F("action", T.STR),
            F("changed_by", T.UUID, fk="users"),
            F("old_value", T.JSON),
            F("new_value", T.JSON),
            F("source_type", T.STR),
            F("changed_at", T.DATETIME),
        ],
    )
)

# ---------------------------------------------------------------------------
# Football domain (expanded ERD: db/football_intelligence_expanded.dbml)
# ---------------------------------------------------------------------------

OPPONENT_CLUBS = _register(
    EntitySpec(
        name="opponent_clubs",
        csv_file="opponent_clubs.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("short_name", T.STR),
            F("logo_url", T.STR),
            F("country", T.STR),
            F("city", T.STR),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

OPPONENT_TEAMS = _register(
    EntitySpec(
        name="opponent_teams",
        csv_file="opponent_teams.csv",
        fields=[
            F("id", T.UUID),
            F("opponent_club_id", T.UUID, fk="opponent_clubs"),
            F("name", T.STR),
            F("short_name", T.STR),
            F("team_type", T.STR),
            F("gender", T.STR),
            F("age_group", T.STR),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

PLAYERS = _register(
    EntitySpec(
        name="players",
        csv_file="players.csv",
        fields=[
            F("id", T.UUID),
            F("first_name", T.STR),
            F("last_name", T.STR),
            F("display_name", T.STR),
            F("date_of_birth", T.DATE),
            F("nationality", T.STR),
            F("preferred_foot", T.STR),
            F("height_cm", T.INT),
            F("weight_kg", T.FLOAT),
            F("primary_position_id", T.UUID, fk="player_positions"),
            F("photo_url", T.STR),
            F("external_reference", T.STR),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

TEAM_PLAYERS = _register(
    EntitySpec(
        name="team_players",
        csv_file="team_players.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("player_id", T.UUID, fk="players"),
            F("season_id", T.UUID, fk="seasons"),
            F("squad_number", T.INT),
            F("position_id", T.UUID, fk="player_positions"),
            F("joined_at", T.DATE),
            F("left_at", T.DATE),
            F("is_captain", T.BOOL),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("own_team_id", "player_id", "season_id")],
    )
)

COMPETITION_SEASONS = _register(
    EntitySpec(
        name="competition_seasons",
        csv_file="competition_seasons.csv",
        fields=[
            F("id", T.UUID),
            F("competition_id", T.UUID, fk="competitions"),
            F("season_id", T.UUID, fk="seasons"),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("competition_id", "season_id")],
    )
)

TEAM_COMPETITIONS = _register(
    EntitySpec(
        name="team_competitions",
        csv_file="team_competitions.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("competition_season_id", T.UUID, fk="competition_seasons"),
            F("is_primary", T.BOOL),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("own_team_id", "competition_season_id")],
    )
)

FIXTURES = _register(
    EntitySpec(
        name="fixtures",
        csv_file="fixtures.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("opponent_team_id", T.UUID, fk="opponent_teams"),
            F("competition_season_id", T.UUID, fk="competition_seasons"),
            F("venue_id", T.UUID, fk="venues"),
            F("scheduled_at", T.DATETIME),
            F("venue_side", T.STR),
            F("round_name", T.STR),
            F("matchweek", T.INT),
            F("status", T.STR),
            F("source_type", T.STR),
            F("external_reference", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

MATCHES = _register(
    EntitySpec(
        name="matches",
        csv_file="matches.csv",
        fields=[
            F("id", T.UUID),
            F("fixture_id", T.UUID, fk="fixtures"),
            F("own_score", T.INT),
            F("opponent_score", T.INT),
            F("halftime_own_score", T.INT),
            F("halftime_opponent_score", T.INT),
            F("result", T.STR),
            F("analysis_status", T.STR),
            F("kickoff_at", T.DATETIME),
            F("finished_at", T.DATETIME),
            F("notes", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("fixture_id",)],
    )
)

MATCH_CONTEXTS = _register(
    EntitySpec(
        name="match_contexts",
        csv_file="match_contexts.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("importance", T.STR),
            F("competition_context", T.STR),
            F("schedule_context", T.STR),
            F("travel_context", T.STR),
            F("weather_context", T.STR),
            F("pitch_context", T.STR),
            F("expected_conditions", T.JSON),
            F("analyst_notes", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("match_id",)],
    )
)

MATCH_LINEUPS = _register(
    EntitySpec(
        name="match_lineups",
        csv_file="match_lineups.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("team_scope", T.STR),
            F("formation", T.STR),
            F("lineup_type", T.STR),
            F("confirmed_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

MATCH_LINEUP_PLAYERS = _register(
    EntitySpec(
        name="match_lineup_players",
        csv_file="match_lineup_players.csv",
        fields=[
            F("id", T.UUID),
            F("lineup_id", T.UUID, fk="match_lineups"),
            F("player_id", T.UUID, fk="players"),
            F("opponent_player_name", T.STR),
            F("position_id", T.UUID, fk="player_positions"),
            F("shirt_number", T.INT),
            F("is_starter", T.BOOL),
            F("minute_on", T.INT),
            F("minute_off", T.INT),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

MATCH_EVENTS = _register(
    EntitySpec(
        name="match_events",
        csv_file="match_events.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("team_scope", T.STR),
            F("player_id", T.UUID, fk="players"),
            F("event_type", T.STR),
            F("minute", T.INT),
            F("second", T.INT),
            F("period", T.STR),
            F("x", T.FLOAT),
            F("y", T.FLOAT),
            F("outcome", T.STR),
            F("details", T.JSON),
            F("source_type", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
        ],
    )
)

PLAYER_MATCH_STATS = _register(
    EntitySpec(
        name="player_match_stats",
        csv_file="player_match_stats.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("player_id", T.UUID, fk="players"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("minutes_played", T.INT),
            F("started", T.BOOL),
            F("goals", T.INT),
            F("assists", T.INT),
            F("shots", T.INT),
            F("shots_on_target", T.INT),
            F("passes_attempted", T.INT),
            F("passes_completed", T.INT),
            F("tackles", T.INT),
            F("interceptions", T.INT),
            F("clearances", T.INT),
            F("touches", T.INT),
            F("yellow_cards", T.INT),
            F("red_cards", T.INT),
            F("xg", T.FLOAT),
            F("xa", T.FLOAT),
            F("extended_stats", T.JSON),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("match_id", "player_id")],
    )
)

TEAM_MATCH_STATS = _register(
    EntitySpec(
        name="team_match_stats",
        csv_file="team_match_stats.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("team_scope", T.STR),
            F("possession_pct", T.FLOAT),
            F("shots", T.INT),
            F("shots_on_target", T.INT),
            F("passes_attempted", T.INT),
            F("passes_completed", T.INT),
            F("pass_completion_pct", T.FLOAT),
            F("corners", T.INT),
            F("fouls", T.INT),
            F("offsides", T.INT),
            F("yellow_cards", T.INT),
            F("red_cards", T.INT),
            F("xg", T.FLOAT),
            F("extended_stats", T.JSON),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("match_id", "team_scope")],
    )
)

PLAYER_SEASON_STATS = _register(
    EntitySpec(
        name="player_season_stats",
        csv_file="player_season_stats.csv",
        fields=[
            F("id", T.UUID),
            F("player_id", T.UUID, fk="players"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("season_id", T.UUID, fk="seasons"),
            F("competition_id", T.UUID, fk="competitions"),
            F("appearances", T.INT),
            F("starts", T.INT),
            F("minutes_played", T.INT),
            F("goals", T.INT),
            F("assists", T.INT),
            F("xg", T.FLOAT),
            F("xa", T.FLOAT),
            F("extended_stats", T.JSON),
            F("calculated_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("player_id", "own_team_id", "season_id", "competition_id")],
    )
)

TEAM_SEASON_STATS = _register(
    EntitySpec(
        name="team_season_stats",
        csv_file="team_season_stats.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("season_id", T.UUID, fk="seasons"),
            F("competition_id", T.UUID, fk="competitions"),
            F("matches_played", T.INT),
            F("wins", T.INT),
            F("draws", T.INT),
            F("losses", T.INT),
            F("goals_for", T.INT),
            F("goals_against", T.INT),
            F("xg_for", T.FLOAT),
            F("xg_against", T.FLOAT),
            F("extended_stats", T.JSON),
            F("calculated_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("own_team_id", "season_id", "competition_id")],
    )
)

PLAYER_AVAILABILITY = _register(
    EntitySpec(
        name="player_availability",
        csv_file="player_availability.csv",
        fields=[
            F("id", T.UUID),
            F("player_id", T.UUID, fk="players"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("availability_status", T.STR),
            F("reason_type", T.STR),
            F("reason", T.STR),
            F("start_date", T.DATE),
            F("expected_return_date", T.DATE),
            F("actual_return_date", T.DATE),
            F("medical_notes", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

SCOUTING_NOTES = _register(
    EntitySpec(
        name="scouting_notes",
        csv_file="scouting_notes.csv",
        fields=[
            F("id", T.UUID),
            F("player_id", T.UUID, fk="players"),
            F("opponent_team_id", T.UUID, fk="opponent_teams"),
            F("match_id", T.UUID, fk="matches"),
            F("author_id", T.UUID, fk="users"),
            F("note_type", T.STR),
            F("title", T.STR),
            F("notes", T.STR),
            F("tags", T.JSON),
            F("visibility", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

OPPOSITION_ANALYSES = _register(
    EntitySpec(
        name="opposition_analyses",
        csv_file="opposition_analyses.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("opponent_team_id", T.UUID, fk="opponent_teams"),
            F("analyst_id", T.UUID, fk="users"),
            F("summary", T.STR),
            F("strengths", T.JSON),
            F("weaknesses", T.JSON),
            F("attacking_patterns", T.JSON),
            F("defensive_patterns", T.JSON),
            F("transition_patterns", T.JSON),
            F("key_players", T.JSON),
            F("threats", T.JSON),
            F("opportunities", T.JSON),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

TACTICAL_PLANS = _register(
    EntitySpec(
        name="tactical_plans",
        csv_file="tactical_plans.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("created_by", T.UUID, fk="users"),
            F("formation", T.STR),
            F("game_model", T.STR),
            F("in_possession_plan", T.STR),
            F("out_of_possession_plan", T.STR),
            F("transition_plan", T.STR),
            F("pressing_plan", T.STR),
            F("notes", T.STR),
            F("status", T.STR),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

SET_PIECE_PLANS = _register(
    EntitySpec(
        name="set_piece_plans",
        csv_file="set_piece_plans.csv",
        fields=[
            F("id", T.UUID),
            F("match_id", T.UUID, fk="matches"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("phase", T.STR),
            F("set_piece_type", T.STR),
            F("title", T.STR),
            F("instructions", T.STR),
            F("assignments", T.JSON),
            F("created_by", T.UUID, fk="users"),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

TEAM_DYNAMICS_ASSESSMENTS = _register(
    EntitySpec(
        name="team_dynamics_assessments",
        csv_file="team_dynamics_assessments.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("season_id", T.UUID, fk="seasons"),
            F("assessed_at", T.DATETIME),
            F("assessed_by", T.UUID, fk="users"),
            F("cohesion_score", T.FLOAT),
            F("chemistry_score", T.FLOAT),
            F("leadership_score", T.FLOAT),
            F("morale_score", T.FLOAT),
            F("notes", T.STR),
            F("evidence", T.JSON),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

PLAYER_RELATIONSHIPS = _register(
    EntitySpec(
        name="player_relationships",
        csv_file="player_relationships.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("player_a_id", T.UUID, fk="players"),
            F("player_b_id", T.UUID, fk="players"),
            F("relationship_type", T.STR),
            F("score", T.FLOAT),
            F("sample_size", T.INT),
            F("evidence", T.JSON),
            F("calculated_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
        unique=[("own_team_id", "player_a_id", "player_b_id", "relationship_type")],
    )
)

UNIT_COHESION = _register(
    EntitySpec(
        name="unit_cohesion",
        csv_file="unit_cohesion.csv",
        fields=[
            F("id", T.UUID),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("season_id", T.UUID, fk="seasons"),
            F("unit_type", T.STR),
            F("unit_name", T.STR),
            F("score", T.FLOAT),
            F("evidence", T.JSON),
            F("calculated_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

ANALYTICS_SNAPSHOTS = _register(
    EntitySpec(
        name="analytics_snapshots",
        csv_file="analytics_snapshots.csv",
        fields=[
            F("id", T.UUID),
            F("home_club_id", T.UUID, fk="home_clubs"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("match_id", T.UUID, fk="matches"),
            F("player_id", T.UUID, fk="players"),
            F("analytics_type", T.STR),
            F("scope_type", T.STR),
            F("title", T.STR),
            F("metrics", T.JSON),
            F("explanation", T.STR),
            F("model_version", T.STR),
            F("calculated_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
        ],
    )
)

RECOMMENDATIONS = _register(
    EntitySpec(
        name="recommendations",
        csv_file="recommendations.csv",
        fields=[
            F("id", T.UUID),
            F("home_club_id", T.UUID, fk="home_clubs"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("match_id", T.UUID, fk="matches"),
            F("player_id", T.UUID, fk="players"),
            F("recommendation_type", T.STR),
            F("title", T.STR),
            F("recommendation", T.STR),
            F("rationale", T.STR),
            F("priority", T.STR),
            F("confidence", T.FLOAT),
            F("status", T.STR),
            F("generated_by", T.STR),
            F("created_by", T.UUID, fk="users"),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

REPORTS = _register(
    EntitySpec(
        name="reports",
        csv_file="reports.csv",
        fields=[
            F("id", T.UUID),
            F("home_club_id", T.UUID, fk="home_clubs"),
            F("own_team_id", T.UUID, fk="own_teams"),
            F("match_id", T.UUID, fk="matches"),
            F("player_id", T.UUID, fk="players"),
            F("report_type", T.STR),
            F("title", T.STR),
            F("content", T.JSON),
            F("status", T.STR),
            F("created_by", T.UUID, fk="users"),
            F("approved_by", T.UUID, fk="users"),
            F("approved_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

DATA_SOURCES = _register(
    EntitySpec(
        name="data_sources",
        csv_file="data_sources.csv",
        fields=[
            F("id", T.UUID),
            F("name", T.STR),
            F("source_type", T.STR),
            F("provider", T.STR),
            F("base_url", T.STR),
            F("is_active", T.BOOL),
            F("configuration", T.JSON),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)

DATA_IMPORTS = _register(
    EntitySpec(
        name="data_imports",
        csv_file="data_imports.csv",
        fields=[
            F("id", T.UUID),
            F("data_source_id", T.UUID, fk="data_sources"),
            F("home_club_id", T.UUID, fk="home_clubs"),
            F("import_type", T.STR),
            F("file_name", T.STR),
            F("external_reference", T.STR),
            F("status", T.STR),
            F("records_received", T.INT),
            F("records_processed", T.INT),
            F("records_failed", T.INT),
            F("error_details", T.JSON),
            F("imported_by", T.UUID, fk="users"),
            F("started_at", T.DATETIME),
            F("completed_at", T.DATETIME),
            F("created_at", T.DATETIME, auto_now_add=True),
            F("updated_at", T.DATETIME, auto_now=True),
        ],
    )
)
