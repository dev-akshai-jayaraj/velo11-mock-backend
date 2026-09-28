from app.api.router_factory import build_crud_router
from app.crud.competition import team_competition
from app.schemas.competition import TeamCompetitionCreate, TeamCompetitionRead, TeamCompetitionUpdate

router = build_crud_router(
    crud=team_competition,
    read_schema=TeamCompetitionRead,
    create_schema=TeamCompetitionCreate,
    update_schema=TeamCompetitionUpdate,
    prefix="/team-competitions",
    tags=["Team Competitions"],
)
