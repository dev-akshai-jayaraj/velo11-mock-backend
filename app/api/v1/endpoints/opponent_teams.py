from app.api.router_factory import build_crud_router
from app.crud.opponent import opponent_team
from app.schemas.opponent import OpponentTeamCreate, OpponentTeamRead, OpponentTeamUpdate

router = build_crud_router(
    crud=opponent_team,
    read_schema=OpponentTeamRead,
    create_schema=OpponentTeamCreate,
    update_schema=OpponentTeamUpdate,
    prefix="/opponent-teams",
    tags=["Opponent Teams"],
)
