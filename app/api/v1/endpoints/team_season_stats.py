from app.api.router_factory import build_crud_router
from app.crud.stats import team_season_stat
from app.schemas.stats import TeamSeasonStatCreate, TeamSeasonStatRead, TeamSeasonStatUpdate

router = build_crud_router(
    crud=team_season_stat,
    read_schema=TeamSeasonStatRead,
    create_schema=TeamSeasonStatCreate,
    update_schema=TeamSeasonStatUpdate,
    prefix="/team-season-stats",
    tags=["Team Season Stats"],
)
