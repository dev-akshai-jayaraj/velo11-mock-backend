from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics_snapshots,
    approval_actions,
    approval_requests,
    approval_stage_approvers,
    approval_stages,
    approval_workflows,
    audit_logs,
    competition_seasons,
    competitions,
    data_imports,
    data_sources,
    fixtures,
    home_clubs,
    match_contexts,
    match_events,
    match_lineup_players,
    match_lineups,
    matches,
    opponent_clubs,
    opponent_teams,
    opposition_analyses,
    own_teams,
    permissions,
    player_availability,
    player_match_stats,
    player_positions,
    player_relationships,
    player_season_stats,
    players,
    recommendations,
    reports,
    role_permissions,
    roles,
    scouting_notes,
    seasons,
    set_piece_plans,
    system_modules,
    tactical_plans,
    team_competitions,
    team_dynamics_assessments,
    team_match_stats,
    team_players,
    team_season_stats,
    unit_cohesion,
    user_roles,
    users,
    venues,
)

api_router = APIRouter()

# Foundation
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

# Squad and opposition
api_router.include_router(players.router)
api_router.include_router(team_players.router)
api_router.include_router(player_availability.router)
api_router.include_router(opponent_clubs.router)
api_router.include_router(opponent_teams.router)
api_router.include_router(competition_seasons.router)
api_router.include_router(team_competitions.router)

# Fixtures and matches
api_router.include_router(fixtures.router)
api_router.include_router(matches.router)
api_router.include_router(match_contexts.router)
api_router.include_router(match_lineups.router)
api_router.include_router(match_lineup_players.router)
api_router.include_router(match_events.router)

# Statistics
api_router.include_router(player_match_stats.router)
api_router.include_router(team_match_stats.router)
api_router.include_router(player_season_stats.router)
api_router.include_router(team_season_stats.router)

# Match preparation
api_router.include_router(scouting_notes.router)
api_router.include_router(opposition_analyses.router)
api_router.include_router(tactical_plans.router)
api_router.include_router(set_piece_plans.router)

# Team dynamics
api_router.include_router(team_dynamics_assessments.router)
api_router.include_router(player_relationships.router)
api_router.include_router(unit_cohesion.router)

# Analytics, recommendations and reporting
api_router.include_router(analytics_snapshots.router)
api_router.include_router(recommendations.router)
api_router.include_router(reports.router)

# Data ingestion
api_router.include_router(data_sources.router)
api_router.include_router(data_imports.router)
