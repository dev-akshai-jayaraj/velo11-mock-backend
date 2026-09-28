from app.api.router_factory import build_crud_router
from app.crud.match import match
from app.schemas.match import MatchCreate, MatchRead, MatchUpdate

router = build_crud_router(
    crud=match,
    read_schema=MatchRead,
    create_schema=MatchCreate,
    update_schema=MatchUpdate,
    prefix="/matches",
    tags=["Matches"],
)
