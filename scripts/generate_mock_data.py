"""Generates the mock CSV dataset under DATA_DIR for every entity in the ERD.

Run from the project root: `uv run python scripts/generate_mock_data.py`

Writes rows directly through app.store.csv_engine using the same EntitySpec
registry the running app reads from, and builds tables in FK-dependency order
so every foreign key in the generated data points at a row that actually
exists elsewhere in the dataset. Re-running this script overwrites all CSVs
under DATA_DIR with a fresh, consistent dataset.
"""

import random
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

# ===========================================================================
# Football domain (expanded ERD)
# ===========================================================================
rng = random.Random(42)  # fixed seed so the generated stats are reproducible
pos_by_code = {p["code"]: p["id"] for p in player_positions}
active_season_id = ids["seasons"][2]
first_team_ids = ids["own_teams"][0::2]  # the "First Team" of each club
focus_team_id = first_team_ids[0]  # Manchester Reds First Team: gets the full match dataset
focus_club_id = ids["home_clubs"][0]
analyst_id, coach_id = ids["users"][0], ids["users"][1]

# ---------------------------------------------------------------------------
# Opponent Clubs / Opponent Teams
# ---------------------------------------------------------------------------
opponent_clubs = [
    dict(name="Northbridge Rovers", short_name="NBR", country="England", city="Newcastle"),
    dict(name="Southport Athletic", short_name="SPA", country="England", city="Southampton"),
    dict(name="Midlands United", short_name="MDU", country="England", city="Birmingham"),
    dict(name="Riverside Town", short_name="RST", country="England", city="Nottingham"),
]
for c in opponent_clubs:
    c.update(id=uid(), logo_url=f"https://example.com/logos/{c['short_name'].lower()}.png",
             status="ACTIVE", created_at=NOW, updated_at=NOW)
ids["opponent_clubs"] = [c["id"] for c in opponent_clubs]
write("opponent_clubs", opponent_clubs)

opponent_teams = [
    dict(id=uid(), opponent_club_id=c["id"], name=f"{c['name']} First Team",
         short_name=f"{c['short_name']} 1st", team_type="SENIOR", gender="MALE",
         age_group="SENIOR", status="ACTIVE", created_at=NOW, updated_at=NOW)
    for c in opponent_clubs
]
ids["opponent_teams"] = [t["id"] for t in opponent_teams]
write("opponent_teams", opponent_teams)

# ---------------------------------------------------------------------------
# Players / Team Players (an 11-player squad for every first team, active season)
# ---------------------------------------------------------------------------
squad_template = [
    ("GK", 1), ("RB", 2), ("CB", 4), ("CB", 5), ("LB", 3), ("CDM", 6),
    ("CM", 8), ("CAM", 10), ("RW", 7), ("LW", 11), ("ST", 9),
]
first_names = ["Oliver", "Harry", "Jack", "Charlie", "George", "Thomas", "James",
               "William", "Noah", "Leo", "Oscar", "Archie", "Henry", "Freddie",
               "Theo", "Alfie", "Arthur", "Isaac", "Lucas", "Mason", "Ethan",
               "Samuel", "Daniel", "Joseph", "Max", "Finley", "Adam", "Ryan",
               "Callum", "Jude", "Reece", "Kai", "Owen"]
last_names = ["Smith", "Jones", "Taylor", "Brown", "Wilson", "Evans", "Walker",
              "Wright", "Robinson", "Thompson", "White", "Hughes", "Edwards",
              "Green", "Hall", "Wood", "Harris", "Clarke", "Lewis", "Jackson",
              "Turner", "Hill", "Moore", "Cooper", "Ward", "Morris", "King",
              "Watson", "Baker", "Young", "Allen", "Wright", "Scott"]
nationalities = ["England", "Scotland", "Wales", "Ireland", "France", "Spain", "Brazil"]

players, team_players = [], []
squad_by_team: dict[uuid.UUID, list[dict]] = {}
n = 0
for team_id in first_team_ids:
    squad_by_team[team_id] = []
    for idx, (code, shirt) in enumerate(squad_template):
        first, last = first_names[n], last_names[n]
        n += 1
        player = dict(
            id=uid(), first_name=first, last_name=last, display_name=f"{first[0]}. {last}",
            date_of_birth=date(1994 + rng.randint(0, 10), rng.randint(1, 12), rng.randint(1, 28)),
            nationality=rng.choice(nationalities), preferred_foot=rng.choice(["RIGHT", "RIGHT", "LEFT"]),
            height_cm=rng.randint(170, 195), weight_kg=round(rng.uniform(65, 90), 1),
            primary_position_id=pos_by_code[code], photo_url=None,
            external_reference=f"EXT-PLY-{n:04d}", status="ACTIVE", created_at=NOW, updated_at=NOW,
        )
        players.append(player)
        squad_by_team[team_id].append(player | {"shirt": shirt, "code": code})
        team_players.append(dict(
            id=uid(), own_team_id=team_id, player_id=player["id"], season_id=active_season_id,
            squad_number=shirt, position_id=pos_by_code[code], joined_at=date(2025, 7, 1),
            left_at=None, is_captain=(code == "CM"), status="ACTIVE", created_at=NOW, updated_at=NOW,
        ))
ids["players"] = [p["id"] for p in players]
write("players", players)
write("team_players", team_players)
focus_squad = squad_by_team[focus_team_id]

# ---------------------------------------------------------------------------
# Competition Seasons / Team Competitions
# ---------------------------------------------------------------------------
competition_seasons = [
    dict(competition_id=ids["competitions"][0], season_id=ids["seasons"][1]),  # PL 24/25
    dict(competition_id=ids["competitions"][0], season_id=active_season_id),   # PL 25/26
    dict(competition_id=ids["competitions"][1], season_id=active_season_id),   # FA Cup 25/26
]
for cs in competition_seasons:
    cs.update(id=uid(), status="ACTIVE", created_at=NOW, updated_at=NOW)
ids["competition_seasons"] = [cs["id"] for cs in competition_seasons]
write("competition_seasons", competition_seasons)
league_cs_id, cup_cs_id = ids["competition_seasons"][1], ids["competition_seasons"][2]

team_competitions = []
for team_id in first_team_ids:
    team_competitions.append(dict(id=uid(), own_team_id=team_id, competition_season_id=league_cs_id,
                                  is_primary=True, status="ACTIVE", created_at=NOW, updated_at=NOW))
    team_competitions.append(dict(id=uid(), own_team_id=team_id, competition_season_id=cup_cs_id,
                                  is_primary=False, status="ACTIVE", created_at=NOW, updated_at=NOW))
write("team_competitions", team_competitions)

# ---------------------------------------------------------------------------
# Fixtures / Matches (focus team: 3 played, 1 upcoming)
# ---------------------------------------------------------------------------
fixture_defs = [
    # opponent idx, competition_season, venue_side, days from NOW, matchweek, score or None
    (0, league_cs_id, "HOME", -21, 1, (2, 1)),
    (1, league_cs_id, "AWAY", -14, 2, (0, 0)),
    (2, cup_cs_id, "HOME", -7, None, (1, 3)),
    (3, league_cs_id, "AWAY", 5, 3, None),
]
fixtures, matches = [], []
for opp_idx, cs_id, side, days, mw, score in fixture_defs:
    kickoff = NOW + timedelta(days=days, hours=6)
    fixture = dict(
        id=uid(), own_team_id=focus_team_id, opponent_team_id=ids["opponent_teams"][opp_idx],
        competition_season_id=cs_id, venue_id=ids["venues"][0] if side == "HOME" else None,
        scheduled_at=kickoff, venue_side=side,
        round_name="Third Round" if cs_id == cup_cs_id else f"Matchweek {mw}", matchweek=mw,
        status="COMPLETED" if score else "SCHEDULED", source_type="MANUAL",
        external_reference=None, created_at=NOW, updated_at=NOW,
    )
    fixtures.append(fixture)
    own, opp = score if score else (None, None)
    result = None if score is None else ("WIN" if own > opp else "LOSS" if own < opp else "DRAW")
    matches.append(dict(
        id=uid(), fixture_id=fixture["id"], own_score=own, opponent_score=opp,
        halftime_own_score=None if score is None else min(own, 1),
        halftime_opponent_score=None if score is None else min(opp, 1),
        result=result, analysis_status="POST_MATCH_COMPLETE" if score else "PRE_MATCH",
        kickoff_at=kickoff if score else None,
        finished_at=kickoff + timedelta(minutes=110) if score else None,
        notes=None, created_at=NOW, updated_at=NOW,
    ))
ids["fixtures"] = [f["id"] for f in fixtures]
ids["matches"] = [m["id"] for m in matches]
write("fixtures", fixtures)
write("matches", matches)
played_matches = [m for m in matches if m["result"] is not None]
upcoming_match = matches[3]

# ---------------------------------------------------------------------------
# Match Contexts
# ---------------------------------------------------------------------------
match_contexts = []
for m, (_, cs_id, side, *_rest) in zip(matches, fixture_defs):
    match_contexts.append(dict(
        id=uid(), match_id=m["id"], importance="HIGH" if cs_id == cup_cs_id else "MEDIUM",
        competition_context="Cup tie, single leg" if cs_id == cup_cs_id else "League fixture",
        schedule_context="Third match in 8 days", travel_context=None if side == "HOME" else "Coach travel, 3h",
        weather_context="Light rain expected", pitch_context="Well-maintained grass",
        expected_conditions={"temperature_c": 12, "wind_kph": 18, "rain_probability": 0.6},
        analyst_notes=None, created_at=NOW, updated_at=NOW,
    ))
write("match_contexts", match_contexts)

# ---------------------------------------------------------------------------
# Match Lineups / Lineup Players (first played match: both sides)
# ---------------------------------------------------------------------------
first_match = played_matches[0]
own_lineup = dict(id=uid(), match_id=first_match["id"], team_scope="OWN", formation="4-2-3-1",
                  lineup_type="STARTING", confirmed_at=first_match["kickoff_at"] - timedelta(hours=1),
                  created_at=NOW, updated_at=NOW)
opp_lineup = dict(id=uid(), match_id=first_match["id"], team_scope="OPPONENT", formation="4-4-2",
                  lineup_type="STARTING", confirmed_at=first_match["kickoff_at"] - timedelta(hours=1),
                  created_at=NOW, updated_at=NOW)
write("match_lineups", [own_lineup, opp_lineup])

lineup_players = []
for p in focus_squad:
    lineup_players.append(dict(
        id=uid(), lineup_id=own_lineup["id"], player_id=p["id"], opponent_player_name=None,
        position_id=pos_by_code[p["code"]], shirt_number=p["shirt"], is_starter=True,
        minute_on=0, minute_off=75 if p["code"] == "LW" else None, created_at=NOW, updated_at=NOW,
    ))
for code, shirt in squad_template:
    lineup_players.append(dict(
        id=uid(), lineup_id=opp_lineup["id"], player_id=None,
        opponent_player_name=f"Opponent #{shirt}", position_id=pos_by_code[code],
        shirt_number=shirt, is_starter=True, minute_on=0, minute_off=None,
        created_at=NOW, updated_at=NOW,
    ))
write("match_lineup_players", lineup_players)

# ---------------------------------------------------------------------------
# Match Events (first played match, 2-1 win)
# ---------------------------------------------------------------------------
striker = next(p for p in focus_squad if p["code"] == "ST")
winger = next(p for p in focus_squad if p["code"] == "RW")
cdm = next(p for p in focus_squad if p["code"] == "CDM")
event_defs = [
    ("OWN", striker, "GOAL", 23, "1H", 88.0, 45.0, "SUCCESS", {"assist_player_id": str(winger["id"])}),
    ("OWN", cdm, "YELLOW_CARD", 38, "1H", 55.0, 30.0, None, {"reason": "Tactical foul"}),
    ("OPPONENT", None, "GOAL", 61, "2H", 12.0, 40.0, "SUCCESS", {"scorer_name": "Opponent #9"}),
    ("OWN", winger, "GOAL", 79, "2H", 84.0, 60.0, "SUCCESS", {"body_part": "LEFT_FOOT"}),
    ("OWN", None, "SUBSTITUTION", 75, "2H", None, None, None, {"note": "LW off, fresh legs"}),
]
match_events = [
    dict(id=uid(), match_id=first_match["id"], team_scope=scope,
         player_id=p["id"] if p else None, event_type=etype, minute=minute, second=0,
         period=period, x=x, y=y, outcome=outcome, details=details, source_type="MANUAL",
         created_at=NOW)
    for scope, p, etype, minute, period, x, y, outcome, details in event_defs
]
write("match_events", match_events)

# ---------------------------------------------------------------------------
# Player / Team Match Stats (every played match)
# ---------------------------------------------------------------------------
player_match_stats, team_match_stats = [], []
for m in played_matches:
    goals_left = m["own_score"]
    for p in focus_squad:
        attacker = p["code"] in ("ST", "RW", "LW", "CAM")
        goals = 0
        if attacker and goals_left:
            goals = 1
            goals_left -= 1
        shots = rng.randint(goals, goals + 3) if attacker else rng.randint(0, 1)
        passes = rng.randint(25, 70)
        player_match_stats.append(dict(
            id=uid(), match_id=m["id"], player_id=p["id"], own_team_id=focus_team_id,
            minutes_played=75 if p["code"] == "LW" else 90, started=True, goals=goals,
            assists=1 if (p["code"] == "RW" and goals_left == 0 and m["own_score"]) else 0,
            shots=shots, shots_on_target=min(shots, goals + rng.randint(0, 1)),
            passes_attempted=passes, passes_completed=int(passes * rng.uniform(0.7, 0.92)),
            tackles=rng.randint(0, 5), interceptions=rng.randint(0, 4), clearances=rng.randint(0, 6),
            touches=rng.randint(30, 90), yellow_cards=0, red_cards=0,
            xg=round(rng.uniform(0.05, 0.8), 2) if attacker else round(rng.uniform(0, 0.1), 2),
            xa=round(rng.uniform(0, 0.4), 2), extended_stats={"progressive_passes": rng.randint(0, 8)},
            created_at=NOW, updated_at=NOW,
        ))
    for scope in ("OWN", "OPPONENT"):
        shots = rng.randint(6, 18)
        passes = rng.randint(350, 600)
        completed = int(passes * rng.uniform(0.75, 0.88))
        possession = round(rng.uniform(45, 62), 1)
        team_match_stats.append(dict(
            id=uid(), match_id=m["id"], team_scope=scope,
            possession_pct=possession if scope == "OWN" else round(100 - possession, 1),
            shots=shots, shots_on_target=rng.randint(2, shots // 2), passes_attempted=passes,
            passes_completed=completed, pass_completion_pct=round(100 * completed / passes, 1),
            corners=rng.randint(2, 9), fouls=rng.randint(6, 15), offsides=rng.randint(0, 4),
            yellow_cards=rng.randint(0, 3), red_cards=0, xg=round(rng.uniform(0.6, 2.4), 2),
            extended_stats={"ppda": round(rng.uniform(7, 14), 1)}, created_at=NOW, updated_at=NOW,
        ))
write("player_match_stats", player_match_stats)
write("team_match_stats", team_match_stats)

# ---------------------------------------------------------------------------
# Player / Team Season Stats (aggregated from the match stats above, all comps)
# ---------------------------------------------------------------------------
player_season_stats = []
for p in focus_squad:
    rows = [s for s in player_match_stats if s["player_id"] == p["id"]]
    player_season_stats.append(dict(
        id=uid(), player_id=p["id"], own_team_id=focus_team_id, season_id=active_season_id,
        competition_id=None, appearances=len(rows), starts=sum(r["started"] for r in rows),
        minutes_played=sum(r["minutes_played"] for r in rows), goals=sum(r["goals"] for r in rows),
        assists=sum(r["assists"] for r in rows), xg=round(sum(r["xg"] for r in rows), 2),
        xa=round(sum(r["xa"] for r in rows), 2), extended_stats=None, calculated_at=NOW,
        created_at=NOW, updated_at=NOW,
    ))
write("player_season_stats", player_season_stats)

own_team_stats = [s for s in team_match_stats if s["team_scope"] == "OWN"]
opp_team_stats = [s for s in team_match_stats if s["team_scope"] == "OPPONENT"]
team_season_stats = [dict(
    id=uid(), own_team_id=focus_team_id, season_id=active_season_id, competition_id=None,
    matches_played=len(played_matches),
    wins=sum(m["result"] == "WIN" for m in played_matches),
    draws=sum(m["result"] == "DRAW" for m in played_matches),
    losses=sum(m["result"] == "LOSS" for m in played_matches),
    goals_for=sum(m["own_score"] for m in played_matches),
    goals_against=sum(m["opponent_score"] for m in played_matches),
    xg_for=round(sum(s["xg"] for s in own_team_stats), 2),
    xg_against=round(sum(s["xg"] for s in opp_team_stats), 2),
    extended_stats=None, calculated_at=NOW, created_at=NOW, updated_at=NOW,
)]
write("team_season_stats", team_season_stats)

# ---------------------------------------------------------------------------
# Player Availability
# ---------------------------------------------------------------------------
lb = next(p for p in focus_squad if p["code"] == "LB")
player_availability = [
    dict(player_id=lb["id"], availability_status="INJURED", reason_type="INJURY",
         reason="Hamstring strain", start_date=date(2026, 7, 25),
         expected_return_date=date(2026, 8, 15), actual_return_date=None,
         medical_notes="Grade 1 strain, progressing well"),
    dict(player_id=cdm["id"], availability_status="SUSPENDED", reason_type="SUSPENSION",
         reason="Accumulated yellow cards", start_date=date(2026, 8, 1),
         expected_return_date=date(2026, 8, 8), actual_return_date=None, medical_notes=None),
    dict(player_id=winger["id"], availability_status="AVAILABLE", reason_type="ILLNESS",
         reason="Flu", start_date=date(2026, 7, 10), expected_return_date=date(2026, 7, 14),
         actual_return_date=date(2026, 7, 13), medical_notes=None),
]
for a in player_availability:
    a.update(id=uid(), own_team_id=focus_team_id, created_at=NOW, updated_at=NOW)
write("player_availability", player_availability)

# ---------------------------------------------------------------------------
# Scouting Notes / Opposition Analysis / Tactical Plans / Set Piece Plans
# (all prepared for the upcoming match)
# ---------------------------------------------------------------------------
next_opponent_id = ids["opponent_teams"][3]
scouting_notes = [
    dict(player_id=None, opponent_team_id=next_opponent_id, match_id=upcoming_match["id"],
         note_type="TEAM", title="Riverside press triggers",
         notes="Press high on goal kicks; slow to recover shape after losing the ball.",
         tags=["pressing", "transition"], visibility="INTERNAL"),
    dict(player_id=striker["id"], opponent_team_id=None, match_id=None, note_type="PLAYER",
         title="Striker movement", notes="Strong near-post runs; could attack the far post more.",
         tags=["finishing"], visibility="COACHING_STAFF"),
]
for s in scouting_notes:
    s.update(id=uid(), author_id=analyst_id, created_at=NOW, updated_at=NOW)
write("scouting_notes", scouting_notes)

opposition_analyses = [dict(
    id=uid(), match_id=upcoming_match["id"], opponent_team_id=next_opponent_id, analyst_id=analyst_id,
    summary="Compact 4-4-2 that concedes space between the lines when pressing.",
    strengths=["Aerial duels", "Counter-attacks down the left"],
    weaknesses=["Slow centre-backs", "Poor rest defence"],
    attacking_patterns={"primary": "Long balls into the channel", "set_pieces": "Near-post flick-ons"},
    defensive_patterns={"block": "Mid", "line_height": "Medium"},
    transition_patterns={"after_winning": "Direct", "after_losing": "Counter-press 5s"},
    key_players=[{"name": "Opponent #9", "threat": "Target man"}, {"name": "Opponent #11", "threat": "Pace"}],
    threats=["Crosses from the left"], opportunities=["Runs in behind the right-back"],
    created_at=NOW, updated_at=NOW,
)]
write("opposition_analyses", opposition_analyses)

tactical_plans = [dict(
    id=uid(), match_id=upcoming_match["id"], own_team_id=focus_team_id, created_by=coach_id,
    formation="4-3-3", game_model="Positional play",
    in_possession_plan="Build through the pivot, overload the right half-space.",
    out_of_possession_plan="Mid block, force play wide.",
    transition_plan="Immediate counter-press for 5 seconds, then recover.",
    pressing_plan="Press trigger: backward pass to centre-back.",
    notes=None, status="DRAFT", created_at=NOW, updated_at=NOW,
)]
write("tactical_plans", tactical_plans)

set_piece_plans = [
    dict(phase="ATTACKING", set_piece_type="CORNER", title="Near-post flick",
         instructions="Inswinging delivery to the near post; late run to the far post.",
         assignments={"taker": str(winger["id"]), "near_post": str(striker["id"])}),
    dict(phase="DEFENDING", set_piece_type="CORNER", title="Zonal plus two",
         instructions="Six-man zonal line with two markers on the main aerial threats.",
         assignments={"zones": 6, "markers": 2}),
]
for s in set_piece_plans:
    s.update(id=uid(), match_id=upcoming_match["id"], own_team_id=focus_team_id,
             created_by=coach_id, created_at=NOW, updated_at=NOW)
write("set_piece_plans", set_piece_plans)

# ---------------------------------------------------------------------------
# Team Dynamics / Player Relationships / Unit Cohesion
# ---------------------------------------------------------------------------
write("team_dynamics_assessments", [dict(
    id=uid(), own_team_id=focus_team_id, season_id=active_season_id,
    assessed_at=NOW - timedelta(days=2), assessed_by=coach_id, cohesion_score=7.5,
    chemistry_score=7.0, leadership_score=8.0, morale_score=7.8,
    notes="Good response after the cup defeat.", evidence={"training_sessions_observed": 4},
    created_at=NOW, updated_at=NOW,
)])

cb_pair = [p for p in focus_squad if p["code"] == "CB"]
player_relationships = [
    dict(player_a_id=cb_pair[0]["id"], player_b_id=cb_pair[1]["id"], relationship_type="PARTNERSHIP",
         score=0.82, sample_size=3, evidence={"shared_minutes": 270}),
    dict(player_a_id=winger["id"], player_b_id=striker["id"], relationship_type="PASSING_LINK",
         score=0.74, sample_size=3, evidence={"passes_between": 41}),
]
for r in player_relationships:
    r.update(id=uid(), own_team_id=focus_team_id, calculated_at=NOW, created_at=NOW, updated_at=NOW)
write("player_relationships", player_relationships)

unit_cohesion = [
    dict(unit_type="DEFENSE", unit_name="Back four", score=7.9),
    dict(unit_type="MIDFIELD", unit_name="Midfield three", score=7.1),
    dict(unit_type="ATTACK", unit_name="Front three", score=6.8),
]
for u in unit_cohesion:
    u.update(id=uid(), own_team_id=focus_team_id, season_id=active_season_id,
             evidence={"matches": len(played_matches)}, calculated_at=NOW, created_at=NOW, updated_at=NOW)
write("unit_cohesion", unit_cohesion)

# ---------------------------------------------------------------------------
# Analytics Snapshots / Recommendations / Reports
# ---------------------------------------------------------------------------
write("analytics_snapshots", [
    dict(id=uid(), home_club_id=focus_club_id, own_team_id=focus_team_id, match_id=first_match["id"],
         player_id=None, analytics_type="MATCH_PERFORMANCE", scope_type="MATCH",
         title="Post-match performance index",
         metrics={"performance_index": 72.4, "xg_difference": 0.6, "ppda": 9.8},
         explanation="Weighted blend of xG difference, pressing intensity and territory.",
         model_version="v0.1", calculated_at=NOW, created_at=NOW),
    dict(id=uid(), home_club_id=focus_club_id, own_team_id=focus_team_id, match_id=None,
         player_id=striker["id"], analytics_type="PLAYER_FORM", scope_type="PLAYER",
         title="Striker form trend", metrics={"form_score": 7.6, "trend": "UP"},
         explanation="Rolling 3-match form from goals, xG and shots on target.",
         model_version="v0.1", calculated_at=NOW, created_at=NOW),
])

write("recommendations", [
    dict(id=uid(), home_club_id=focus_club_id, own_team_id=focus_team_id, match_id=upcoming_match["id"],
         player_id=None, recommendation_type="TACTICAL", title="Target the right half-space",
         recommendation="Overload the opponent's left side with the RW and CAM.",
         rationale="The opposition's left-back is caught upfield on 40% of their transitions.",
         priority="HIGH", confidence=0.72, status="OPEN", generated_by="SYSTEM",
         created_by=None, created_at=NOW, updated_at=NOW),
    dict(id=uid(), home_club_id=focus_club_id, own_team_id=focus_team_id, match_id=None,
         player_id=lb["id"], recommendation_type="PLAYER_LOAD", title="Manage LB return",
         recommendation="Limit to 60 minutes in first match back.",
         rationale="Returning from a hamstring strain.", priority="MEDIUM", confidence=0.9,
         status="ACCEPTED", generated_by="MANUAL", created_by=coach_id, created_at=NOW, updated_at=NOW),
])

write("reports", [
    dict(id=uid(), home_club_id=focus_club_id, own_team_id=focus_team_id, match_id=first_match["id"],
         player_id=None, report_type="POST_MATCH", title="Post-match report: Matchweek 1",
         content={"summary": "Deserved 2-1 win.", "sections": ["Key moments", "Player ratings"]},
         status="APPROVED", created_by=analyst_id, approved_by=coach_id,
         approved_at=NOW - timedelta(days=19), created_at=NOW, updated_at=NOW),
    dict(id=uid(), home_club_id=focus_club_id, own_team_id=focus_team_id, match_id=upcoming_match["id"],
         player_id=None, report_type="PRE_MATCH", title="Pre-match report: Riverside Town",
         content={"summary": "Opposition overview and game plan."}, status="DRAFT",
         created_by=analyst_id, approved_by=None, approved_at=None, created_at=NOW, updated_at=NOW),
])

# ---------------------------------------------------------------------------
# Data Sources / Data Imports
# ---------------------------------------------------------------------------
data_sources = [
    dict(name="Manual entry", source_type="MANUAL", provider=None, base_url=None, configuration=None),
    dict(name="Match stats CSV upload", source_type="CSV", provider="Internal", base_url=None,
         configuration={"delimiter": ",", "encoding": "utf-8"}),
    dict(name="Fixtures API", source_type="API", provider="ExampleFootballData",
         base_url="https://api.example.com/v1", configuration={"rate_limit_per_min": 60}),
]
for s in data_sources:
    s.update(id=uid(), is_active=True, created_at=NOW, updated_at=NOW)
ids["data_sources"] = [s["id"] for s in data_sources]
write("data_sources", data_sources)

write("data_imports", [
    dict(id=uid(), data_source_id=ids["data_sources"][1], home_club_id=focus_club_id,
         import_type="PLAYER_MATCH_STATS", file_name="matchweek_1_stats.csv", external_reference=None,
         status="COMPLETED", records_received=11, records_processed=11, records_failed=0,
         error_details=None, imported_by=analyst_id, started_at=NOW - timedelta(days=20),
         completed_at=NOW - timedelta(days=20, minutes=-2), created_at=NOW, updated_at=NOW),
    dict(id=uid(), data_source_id=ids["data_sources"][2], home_club_id=focus_club_id,
         import_type="FIXTURES", file_name=None, external_reference="sync-2026-08-01",
         status="PARTIAL", records_received=10, records_processed=8, records_failed=2,
         error_details={"errors": ["Unknown opponent team: 'Eastfield FC'", "Missing kickoff time"]},
         imported_by=None, started_at=NOW - timedelta(hours=1),
         completed_at=NOW - timedelta(minutes=55), created_at=NOW, updated_at=NOW),
])

print()
print(f"Mock dataset written to {DATA_DIR}")
