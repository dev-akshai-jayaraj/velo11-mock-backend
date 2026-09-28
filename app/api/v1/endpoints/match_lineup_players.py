from app.api.router_factory import build_crud_router
from app.crud.match import match_lineup_player
from app.schemas.match import MatchLineupPlayerCreate, MatchLineupPlayerRead, MatchLineupPlayerUpdate

router = build_crud_router(
    crud=match_lineup_player,
    read_schema=MatchLineupPlayerRead,
    create_schema=MatchLineupPlayerCreate,
    update_schema=MatchLineupPlayerUpdate,
    prefix="/match-lineup-players",
    tags=["Match Lineup Players"],
)
