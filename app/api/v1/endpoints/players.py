from app.api.router_factory import build_crud_router
from app.crud.player import player
from app.schemas.player import PlayerCreate, PlayerRead, PlayerUpdate

router = build_crud_router(
    crud=player,
    read_schema=PlayerRead,
    create_schema=PlayerCreate,
    update_schema=PlayerUpdate,
    prefix="/players",
    tags=["Players"],
)
