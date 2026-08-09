"""Generates the mock CSV dataset under DATA_DIR for every entity in the ERD.

Run from the project root: `uv run python scripts/generate_mock_data.py`

Writes rows directly through app.store.csv_engine using the same EntitySpec
registry the running app reads from, and builds tables in FK-dependency order
so every foreign key in the generated data points at a row that actually
exists elsewhere in the dataset. Re-running this script overwrites all CSVs
under DATA_DIR with a fresh, consistent dataset.
"""

import sys
import uuid
from datetime import date, datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.store import csv_engine  # noqa: E402
from app.store.registry import REGISTRY  # noqa: E402

DATA_DIR = Path(settings.DATA_DIR)
NOW = datetime(2026, 8, 1, 9, 0, 0)


def uid() -> uuid.UUID:
    return uuid.uuid4()


def write(entity_name: str, rows: list[dict]) -> None:
    spec = REGISTRY[entity_name]
    path = DATA_DIR / spec.csv_file
    csv_engine.write_rows_unlocked(path, spec, rows)
    print(f"  wrote {len(rows):3d} rows -> {path.name}")


ids: dict[str, list[uuid.UUID]] = {}

# ---------------------------------------------------------------------------
# Venues
# ---------------------------------------------------------------------------
venues = [
    dict(name="Old Trafford", country="England", city="Manchester",
         address="Sir Matt Busby Way, Manchester", surface_type="GRASS",
         capacity=74310, is_home_venue=True, status="ACTIVE"),
    dict(name="Anfield", country="England", city="Liverpool",
         address="Anfield Rd, Liverpool", surface_type="GRASS",
         capacity=61276, is_home_venue=True, status="ACTIVE"),
    dict(name="Emirates Stadium", country="England", city="London",
         address="Hornsey Rd, London", surface_type="HYBRID",
         capacity=60704, is_home_venue=True, status="ACTIVE"),
]
for v in venues:
    v.update(id=uid(), created_at=NOW, updated_at=NOW)
ids["venues"] = [v["id"] for v in venues]
write("venues", venues)

# ---------------------------------------------------------------------------
# Home Clubs
# ---------------------------------------------------------------------------
home_clubs = [
    dict(name="Manchester Reds", short_name="MCR", logo_url="https://example.com/logos/mcr.png",
         country="England", timezone="Europe/London", primary_color="#DA291C",
         secondary_color="#FBE122", home_venue_id=ids["venues"][0], status="ACTIVE"),
    dict(name="Liverpool Kickers", short_name="LVK", logo_url="https://example.com/logos/lvk.png",
         country="England", timezone="Europe/London", primary_color="#C8102E",
         secondary_color="#00B2A9", home_venue_id=ids["venues"][1], status="ACTIVE"),
    dict(name="London Gunners", short_name="LDG", logo_url="https://example.com/logos/ldg.png",
         country="England", timezone="Europe/London", primary_color="#EF0107",
         secondary_color="#9C824A", home_venue_id=ids["venues"][2], status="ACTIVE"),
]
for c in home_clubs:
    c.update(id=uid(), created_at=NOW, updated_at=NOW)
ids["home_clubs"] = [c["id"] for c in home_clubs]
write("home_clubs", home_clubs)

# ---------------------------------------------------------------------------
# Own Teams (First Team + U18 per club)
# ---------------------------------------------------------------------------
own_teams = []
team_templates = [
    dict(name_suffix="First Team", short_suffix="1st", team_type="SENIOR", age_group="SENIOR"),
    dict(name_suffix="U18", short_suffix="U18", team_type="YOUTH", age_group="U18"),
]
club_short = ["Manchester Reds", "Liverpool Kickers", "London Gunners"]
for club_id, club_name in zip(ids["home_clubs"], club_short):
    for tpl in team_templates:
        own_teams.append(dict(
            id=uid(), home_club_id=club_id,
            name=f"{club_name} {tpl['name_suffix']}",
            short_name=f"{club_name.split()[0][:3].upper()} {tpl['short_suffix']}",
            team_type=tpl["team_type"], gender="MALE", age_group=tpl["age_group"],
            status="ACTIVE", created_at=NOW, updated_at=NOW,
        ))
ids["own_teams"] = [t["id"] for t in own_teams]
write("own_teams", own_teams)

# ---------------------------------------------------------------------------
# Users (2 per club)
# ---------------------------------------------------------------------------
# Real PBKDF2-SHA256 hash of "ChangeMe123!" via app/core/security.py, so the stored
# value has the same shape production data would (there's no login endpoint yet
# to actually authenticate against it).
DEMO_PASSWORD_HASH = hash_password("ChangeMe123!")
user_names = [
    ("Alex", "Ferguson", "alex.ferguson"), ("Jamie", "Carragher", "jamie.carragher"),
    ("Jurgen", "Klopp", "jurgen.klopp"), ("Steven", "Gerrard", "steven.gerrard"),
    ("Mikel", "Arteta", "mikel.arteta"), ("Ian", "Wright", "ian.wright"),
]
users = []
for i, (first, last, handle) in enumerate(user_names):
    club_id = ids["home_clubs"][i // 2]
    users.append(dict(
        id=uid(), home_club_id=club_id, first_name=first, last_name=last,
        email=f"{handle}@example.com", password_hash=DEMO_PASSWORD_HASH,
        phone=f"+44-7000-0000{i:02d}", status="ACTIVE",
        last_login_at=NOW - timedelta(days=i), created_at=NOW, updated_at=NOW,
    ))
ids["users"] = [u["id"] for u in users]
write("users", users)

# ---------------------------------------------------------------------------
# Roles
# ---------------------------------------------------------------------------
roles = [
    dict(name="Club Administrator", code="CLUB_ADMIN",
         description="Full access to manage club data", is_system_role=False),
    dict(name="Coach", code="COACH", description="Manages own teams and player data",
         is_system_role=False),
    dict(name="Analyst", code="ANALYST", description="Read-only access to reporting data",
         is_system_role=False),
    dict(name="System Owner", code="SYSTEM_OWNER",
         description="Built-in role with unrestricted access", is_system_role=True),
]
for r in roles:
    r.update(id=uid(), created_at=NOW, updated_at=NOW)
ids["roles"] = [r["id"] for r in roles]
write("roles", roles)

# ---------------------------------------------------------------------------
# Permissions
# ---------------------------------------------------------------------------
permission_defs = [
    ("USERS", "CREATE", "Create Users"),
    ("USERS", "READ", "View Users"),
    ("OWN_TEAMS", "CREATE", "Create Own Teams"),
    ("OWN_TEAMS", "UPDATE", "Update Own Teams"),
    ("APPROVALS", "APPROVE", "Approve Requests"),
    ("APPROVALS", "REJECT", "Reject Requests"),
    ("AUDIT", "READ", "View Audit Logs"),
    ("SYSTEM", "CONFIGURE", "Configure System Modules"),
]
permissions = []
for module_code, action_code, name in permission_defs:
    permissions.append(dict(
        id=uid(), module_code=module_code, action_code=action_code, name=name,
        description=f"Allows the '{action_code}' action on the '{module_code}' module",
        created_at=NOW, updated_at=NOW,
    ))
ids["permissions"] = [p["id"] for p in permissions]
write("permissions", permissions)

# ---------------------------------------------------------------------------
# User Roles
# ---------------------------------------------------------------------------
# users[0,2,4] are club admins for their club, users[1,3,5] are coaches
user_roles = []
for i, user_id in enumerate(ids["users"]):
    role_id = ids["roles"][0] if i % 2 == 0 else ids["roles"][1]
    user_roles.append(dict(
        id=uid(), user_id=user_id, role_id=role_id, assigned_at=NOW,
        assigned_by=ids["users"][0],
    ))
# give the first user (a club admin) the analyst role too, to show a user with 2 roles
user_roles.append(dict(
    id=uid(), user_id=ids["users"][0], role_id=ids["roles"][2], assigned_at=NOW,
    assigned_by=ids["users"][0],
))
ids["user_roles"] = [ur["id"] for ur in user_roles]
write("user_roles", user_roles)

# ---------------------------------------------------------------------------
# Role Permissions
# ---------------------------------------------------------------------------
role_permissions = []


def grant(role_idx: int, permission_idx: int):
    role_permissions.append(dict(
        id=uid(), role_id=ids["roles"][role_idx], permission_id=ids["permissions"][permission_idx],
        created_at=NOW,
    ))


# CLUB_ADMIN: everything except SYSTEM/CONFIGURE
for p_idx in range(len(permissions) - 1):
    grant(0, p_idx)
# COACH: read users, manage own teams
grant(1, 1)  # USERS/READ
grant(1, 2)  # OWN_TEAMS/CREATE
grant(1, 3)  # OWN_TEAMS/UPDATE
# ANALYST: read-only
grant(2, 1)  # USERS/READ
grant(2, 6)  # AUDIT/READ
# SYSTEM_OWNER: everything
for p_idx in range(len(permissions)):
    grant(3, p_idx)
ids["role_permissions"] = [rp["id"] for rp in role_permissions]
write("role_permissions", role_permissions)

# ---------------------------------------------------------------------------
# Seasons
# ---------------------------------------------------------------------------
seasons = [
    dict(name="2023/2024", start_date=date(2023, 8, 1), end_date=date(2024, 5, 31),
         is_active=False, status="ACTIVE"),
    dict(name="2024/2025", start_date=date(2024, 8, 1), end_date=date(2025, 5, 31),
         is_active=False, status="ACTIVE"),
    dict(name="2025/2026", start_date=date(2025, 8, 1), end_date=date(2026, 5, 31),
         is_active=True, status="ACTIVE"),
]
for s in seasons:
    s.update(id=uid(), created_at=NOW, updated_at=NOW)
ids["seasons"] = [s["id"] for s in seasons]
write("seasons", seasons)

# ---------------------------------------------------------------------------
# Competitions
# ---------------------------------------------------------------------------
competitions = [
    dict(name="Premier League", type="LEAGUE", country="England", level="TIER_1"),
    dict(name="FA Cup", type="CUP", country="England", level="TIER_1"),
    dict(name="UEFA Champions League", type="CUP", country="Europe", level="TIER_1"),
    dict(name="Championship", type="LEAGUE", country="England", level="TIER_2"),
]
for c in competitions:
    c.update(id=uid(), status="ACTIVE", created_at=NOW, updated_at=NOW)
ids["competitions"] = [c["id"] for c in competitions]
write("competitions", competitions)

# ---------------------------------------------------------------------------
# Player Positions
# ---------------------------------------------------------------------------
position_defs = [
    ("Goalkeeper", "GK", "GOALKEEPER", 1),
    ("Right Back", "RB", "DEFENSE", 2),
    ("Centre Back", "CB", "DEFENSE", 3),
    ("Left Back", "LB", "DEFENSE", 4),
    ("Defensive Midfielder", "CDM", "MIDFIELD", 5),
    ("Central Midfielder", "CM", "MIDFIELD", 6),
    ("Attacking Midfielder", "CAM", "MIDFIELD", 7),
    ("Right Winger", "RW", "ATTACK", 8),
    ("Left Winger", "LW", "ATTACK", 9),
    ("Striker", "ST", "ATTACK", 10),
]
player_positions = []
for name, code, group, order in position_defs:
    player_positions.append(dict(
        id=uid(), name=name, code=code, position_group=group, display_order=order,
        status="ACTIVE", created_at=NOW, updated_at=NOW,
    ))
ids["player_positions"] = [p["id"] for p in player_positions]
write("player_positions", player_positions)

# ---------------------------------------------------------------------------
# System Modules
# ---------------------------------------------------------------------------
system_modules = [
    dict(name="Own Teams", code="OWN_TEAMS", description="Own team management module"),
    dict(name="Users", code="USERS", description="User management module"),
    dict(name="Approvals", code="APPROVALS", description="Approval workflow engine"),
    dict(name="Audit", code="AUDIT", description="Audit logging module"),
]
for m in system_modules:
    m.update(id=uid(), is_active=True, created_at=NOW, updated_at=NOW)
ids["system_modules"] = [m["id"] for m in system_modules]
write("system_modules", system_modules)

# ---------------------------------------------------------------------------
# Approval Workflows (Own Teams + Users)
# ---------------------------------------------------------------------------
approval_workflows = [
    dict(module_id=ids["system_modules"][0], name="Own Team Approval", code="OWN_TEAM_APPROVAL",
         is_required=True),
    dict(module_id=ids["system_modules"][1], name="User Onboarding Approval", code="USER_APPROVAL",
         is_required=True),
]
for w in approval_workflows:
    w.update(id=uid(), is_active=True, created_at=NOW, updated_at=NOW)
ids["approval_workflows"] = [w["id"] for w in approval_workflows]
write("approval_workflows", approval_workflows)

# ---------------------------------------------------------------------------
# Approval Stages (2 per workflow)
# ---------------------------------------------------------------------------
approval_stages = []
for workflow_id in ids["approval_workflows"]:
    approval_stages.append(dict(
        id=uid(), workflow_id=workflow_id, name="Coach Review", stage_order=1,
        approval_type="ANY", is_final_stage=False, created_at=NOW, updated_at=NOW,
    ))
    approval_stages.append(dict(
        id=uid(), workflow_id=workflow_id, name="Admin Final Approval", stage_order=2,
        approval_type="ANY", is_final_stage=True, created_at=NOW, updated_at=NOW,
    ))
ids["approval_stages"] = [s["id"] for s in approval_stages]
write("approval_stages", approval_stages)

# ---------------------------------------------------------------------------
# Approval Stage Approvers
# ---------------------------------------------------------------------------
approval_stage_approvers = []
# stage 0 (own team workflow / coach review) -> COACH role
approval_stage_approvers.append(dict(
    id=uid(), approval_stage_id=ids["approval_stages"][0], role_id=ids["roles"][1],
    user_id=None, approver_type="ROLE", created_at=NOW, updated_at=NOW,
))
# stage 1 (own team workflow / admin final) -> CLUB_ADMIN role
approval_stage_approvers.append(dict(
    id=uid(), approval_stage_id=ids["approval_stages"][1], role_id=ids["roles"][0],
    user_id=None, approver_type="ROLE", created_at=NOW, updated_at=NOW,
))
# stage 2 (user workflow / coach review) -> specific user
approval_stage_approvers.append(dict(
    id=uid(), approval_stage_id=ids["approval_stages"][2], role_id=None,
    user_id=ids["users"][1], approver_type="USER", created_at=NOW, updated_at=NOW,
))
# stage 3 (user workflow / admin final) -> CLUB_ADMIN role
approval_stage_approvers.append(dict(
    id=uid(), approval_stage_id=ids["approval_stages"][3], role_id=ids["roles"][0],
    user_id=None, approver_type="ROLE", created_at=NOW, updated_at=NOW,
))
ids["approval_stage_approvers"] = [a["id"] for a in approval_stage_approvers]
write("approval_stage_approvers", approval_stage_approvers)

# ---------------------------------------------------------------------------
# Approval Requests (own-team workflow requests referencing real own_teams rows)
# ---------------------------------------------------------------------------
approval_requests = [
    dict(workflow_id=ids["approval_workflows"][0], module_id=ids["system_modules"][0],
         record_id=ids["own_teams"][0], record_type="OWN_TEAM", current_status="APPROVED",
         current_stage_order=2, submitted_by=ids["users"][1],
         submitted_at=NOW - timedelta(days=5), completed_at=NOW - timedelta(days=4)),
    dict(workflow_id=ids["approval_workflows"][0], module_id=ids["system_modules"][0],
         record_id=ids["own_teams"][2], record_type="OWN_TEAM", current_status="SUBMITTED",
         current_stage_order=1, submitted_by=ids["users"][3],
         submitted_at=NOW - timedelta(days=1), completed_at=None),
    dict(workflow_id=ids["approval_workflows"][0], module_id=ids["system_modules"][0],
         record_id=ids["own_teams"][4], record_type="OWN_TEAM", current_status="REJECTED",
         current_stage_order=1, submitted_by=ids["users"][5],
         submitted_at=NOW - timedelta(days=10), completed_at=NOW - timedelta(days=9)),
    dict(workflow_id=ids["approval_workflows"][1], module_id=ids["system_modules"][1],
         record_id=ids["users"][4], record_type="USER", current_status="IN_REVIEW",
         current_stage_order=1, submitted_by=ids["users"][2],
         submitted_at=NOW - timedelta(days=2), completed_at=None),
    dict(workflow_id=ids["approval_workflows"][1], module_id=ids["system_modules"][1],
         record_id=ids["users"][5], record_type="USER", current_status="APPROVED",
         current_stage_order=2, submitted_by=ids["users"][2],
         submitted_at=NOW - timedelta(days=7), completed_at=NOW - timedelta(days=6)),
]
for r in approval_requests:
    r.update(id=uid(), created_at=NOW, updated_at=NOW)
ids["approval_requests"] = [r["id"] for r in approval_requests]
write("approval_requests", approval_requests)

# ---------------------------------------------------------------------------
# Approval Actions
# ---------------------------------------------------------------------------
approval_actions = [
    dict(approval_request_id=ids["approval_requests"][0], approval_stage_id=ids["approval_stages"][0],
         action_by=ids["users"][1], action="APPROVE", comments="Roster looks good",
         action_at=NOW - timedelta(days=5)),
    dict(approval_request_id=ids["approval_requests"][0], approval_stage_id=ids["approval_stages"][1],
         action_by=ids["users"][0], action="APPROVE", comments="Confirmed, approved",
         action_at=NOW - timedelta(days=4)),
    dict(approval_request_id=ids["approval_requests"][1], approval_stage_id=ids["approval_stages"][0],
         action_by=ids["users"][3], action="COMMENT", comments="Awaiting coach review",
         action_at=NOW - timedelta(days=1)),
    dict(approval_request_id=ids["approval_requests"][2], approval_stage_id=ids["approval_stages"][0],
         action_by=ids["users"][5], action="REJECT", comments="Squad size exceeds limit",
         action_at=NOW - timedelta(days=9)),
    dict(approval_request_id=ids["approval_requests"][4], approval_stage_id=ids["approval_stages"][2],
         action_by=ids["users"][1], action="APPROVE", comments="Reference check complete",
         action_at=NOW - timedelta(days=7)),
    dict(approval_request_id=ids["approval_requests"][4], approval_stage_id=ids["approval_stages"][3],
         action_by=ids["users"][0], action="APPROVE", comments="Onboarding approved",
         action_at=NOW - timedelta(days=6)),
]
for a in approval_actions:
    a.update(id=uid())
ids["approval_actions"] = [a["id"] for a in approval_actions]
write("approval_actions", approval_actions)

# ---------------------------------------------------------------------------
# Audit Logs
# ---------------------------------------------------------------------------
audit_logs = [
    dict(module_code="OWN_TEAMS", record_id=ids["own_teams"][0], action="CREATE",
         changed_by=ids["users"][1], old_value=None, new_value={"status": "ACTIVE"},
         source_type="MANUAL", changed_at=NOW - timedelta(days=6)),
    dict(module_code="OWN_TEAMS", record_id=ids["own_teams"][0], action="UPDATE",
         changed_by=ids["users"][0], old_value={"status": "ACTIVE"},
         new_value={"status": "ACTIVE", "age_group": "SENIOR"}, source_type="MANUAL",
         changed_at=NOW - timedelta(days=4)),
    dict(module_code="USERS", record_id=ids["users"][4], action="CREATE",
         changed_by=ids["users"][2], old_value=None, new_value={"status": "ACTIVE"},
         source_type="MANUAL", changed_at=NOW - timedelta(days=8)),
    dict(module_code="APPROVALS", record_id=ids["approval_requests"][2], action="UPDATE",
         changed_by=ids["users"][5], old_value={"current_status": "SUBMITTED"},
         new_value={"current_status": "REJECTED"}, source_type="SYSTEM",
         changed_at=NOW - timedelta(days=9)),
    dict(module_code="ROLES", record_id=ids["roles"][0], action="UPDATE",
         changed_by=ids["users"][0], old_value={"description": None},
         new_value={"description": "Full access to manage club data"}, source_type="MANUAL",
         changed_at=NOW - timedelta(days=20)),
    dict(module_code="USERS", record_id=ids["users"][5], action="UPDATE",
         changed_by=ids["users"][2], old_value={"status": "PENDING"},
         new_value={"status": "ACTIVE"}, source_type="SYSTEM",
         changed_at=NOW - timedelta(days=6)),
    dict(module_code="OWN_TEAMS", record_id=ids["own_teams"][4], action="DELETE",
         changed_by=ids["users"][5], old_value={"status": "ACTIVE"}, new_value=None,
         source_type="MANUAL", changed_at=NOW - timedelta(days=3)),
    dict(module_code="SYSTEM_MODULES", record_id=ids["system_modules"][2], action="CREATE",
         changed_by=ids["users"][0], old_value=None, new_value={"is_active": True},
         source_type="MANUAL", changed_at=NOW - timedelta(days=30)),
]
for log in audit_logs:
    log.update(id=uid())
write("audit_logs", audit_logs)

print()
print(f"Mock dataset written to {DATA_DIR}")
