from app.api.router_factory import build_crud_router
from app.crud.dynamics import player_relationship
from app.schemas.dynamics import PlayerRelationshipCreate, PlayerRelationshipRead, PlayerRelationshipUpdate

router = build_crud_router(
    crud=player_relationship,
    read_schema=PlayerRelationshipRead,
    create_schema=PlayerRelationshipCreate,
    update_schema=PlayerRelationshipUpdate,
    prefix="/player-relationships",
    tags=["Player Relationships"],
)
