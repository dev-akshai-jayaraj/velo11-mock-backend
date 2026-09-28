from app.api.router_factory import build_crud_router
from app.crud.match import match_context
from app.schemas.match import MatchContextCreate, MatchContextRead, MatchContextUpdate

router = build_crud_router(
    crud=match_context,
    read_schema=MatchContextRead,
    create_schema=MatchContextCreate,
    update_schema=MatchContextUpdate,
    prefix="/match-contexts",
    tags=["Match Contexts"],
)
