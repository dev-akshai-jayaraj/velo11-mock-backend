from app.api.router_factory import build_crud_router
from app.crud.stats import player_match_stat
from app.schemas.stats import PlayerMatchStatCreate, PlayerMatchStatRead, PlayerMatchStatUpdate

router = build_crud_router(
    crud=player_match_stat,
    read_schema=PlayerMatchStatRead,
    create_schema=PlayerMatchStatCreate,
    update_schema=PlayerMatchStatUpdate,
    prefix="/player-match-stats",
    tags=["Player Match Stats"],
)
