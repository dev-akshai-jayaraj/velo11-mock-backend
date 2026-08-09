from fastapi import APIRouter

from app.api.v1.endpoints import (
    approval_actions,
    approval_requests,
    approval_stage_approvers,
    approval_stages,
    approval_workflows,
    audit_logs,
    competitions,
    home_clubs,
    own_teams,
    permissions,
    player_positions,
    role_permissions,
    roles,
    seasons,
    system_modules,
    user_roles,
    users,
    venues,
)

api_router = APIRouter()

api_router.include_router(home_clubs.router)
api_router.include_router(venues.router)
api_router.include_router(own_teams.router)
api_router.include_router(users.router)
api_router.include_router(roles.router)
api_router.include_router(permissions.router)
api_router.include_router(user_roles.router)
api_router.include_router(role_permissions.router)
api_router.include_router(seasons.router)
api_router.include_router(competitions.router)
api_router.include_router(player_positions.router)
api_router.include_router(system_modules.router)
api_router.include_router(approval_workflows.router)
api_router.include_router(approval_stages.router)
api_router.include_router(approval_stage_approvers.router)
api_router.include_router(approval_requests.router)
api_router.include_router(approval_actions.router)
api_router.include_router(audit_logs.router)
