from app.api.router_factory import build_crud_router
from app.crud.match import match_lineup
from app.schemas.match import MatchLineupCreate, MatchLineupRead, MatchLineupUpdate

router = build_crud_router(
    crud=match_lineup,
    read_schema=MatchLineupRead,
    create_schema=MatchLineupCreate,
    update_schema=MatchLineupUpdate,
    prefix="/match-lineups",
    tags=["Match Lineups"],
)
