from app.api.router_factory import build_crud_router
from app.crud.stats import team_match_stat
from app.schemas.stats import TeamMatchStatCreate, TeamMatchStatRead, TeamMatchStatUpdate

router = build_crud_router(
    crud=team_match_stat,
    read_schema=TeamMatchStatRead,
    create_schema=TeamMatchStatCreate,
    update_schema=TeamMatchStatUpdate,
    prefix="/team-match-stats",
    tags=["Team Match Stats"],
)
