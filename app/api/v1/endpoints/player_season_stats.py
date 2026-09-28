from app.api.router_factory import build_crud_router
from app.crud.stats import player_season_stat
from app.schemas.stats import PlayerSeasonStatCreate, PlayerSeasonStatRead, PlayerSeasonStatUpdate

router = build_crud_router(
    crud=player_season_stat,
    read_schema=PlayerSeasonStatRead,
    create_schema=PlayerSeasonStatCreate,
    update_schema=PlayerSeasonStatUpdate,
    prefix="/player-season-stats",
    tags=["Player Season Stats"],
)
