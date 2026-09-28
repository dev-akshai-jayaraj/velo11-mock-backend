from app.api.router_factory import build_crud_router
from app.crud.match import match_event
from app.schemas.match import MatchEventCreate, MatchEventRead, MatchEventUpdate

router = build_crud_router(
    crud=match_event,
    read_schema=MatchEventRead,
    create_schema=MatchEventCreate,
    update_schema=MatchEventUpdate,
    prefix="/match-events",
    tags=["Match Events"],
)
