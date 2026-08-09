from app.api.router_factory import build_crud_router
from app.crud.competition import player_position
from app.schemas.competition import (
    PlayerPositionCreate,
    PlayerPositionRead,
    PlayerPositionUpdate,
)

router = build_crud_router(
    crud=player_position,
    read_schema=PlayerPositionRead,
    create_schema=PlayerPositionCreate,
    update_schema=PlayerPositionUpdate,
    prefix="/player-positions",
    tags=["Player Positions"],
)
