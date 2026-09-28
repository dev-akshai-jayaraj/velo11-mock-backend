from app.api.router_factory import build_crud_router
from app.crud.player import player_availability
from app.schemas.player import PlayerAvailabilityCreate, PlayerAvailabilityRead, PlayerAvailabilityUpdate

router = build_crud_router(
    crud=player_availability,
    read_schema=PlayerAvailabilityRead,
    create_schema=PlayerAvailabilityCreate,
    update_schema=PlayerAvailabilityUpdate,
    prefix="/player-availability",
    tags=["Player Availability"],
)
