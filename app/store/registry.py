"""Single source of truth for the CSV-backed data model.

Mirrors the tables in db/schema.sql. Both the runtime CsvRepository and the
scripts/generate_mock_data.py generator read this registry, so the on-disk
CSV shape and the mock data can never drift from each other.
"""

from dataclasses import dataclass, field
from enum import Enum


class FieldType(str, Enum):
    STR = "str"
    INT = "int"
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
