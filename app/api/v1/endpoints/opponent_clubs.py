from app.api.router_factory import build_crud_router
from app.crud.opponent import opponent_club
from app.schemas.opponent import OpponentClubCreate, OpponentClubRead, OpponentClubUpdate

router = build_crud_router(
    crud=opponent_club,
    read_schema=OpponentClubRead,
    create_schema=OpponentClubCreate,
    update_schema=OpponentClubUpdate,
    prefix="/opponent-clubs",
    tags=["Opponent Clubs"],
)
