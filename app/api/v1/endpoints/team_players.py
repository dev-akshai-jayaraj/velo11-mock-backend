from app.api.router_factory import build_crud_router
from app.crud.player import team_player
from app.schemas.player import TeamPlayerCreate, TeamPlayerRead, TeamPlayerUpdate

router = build_crud_router(
    crud=team_player,
    read_schema=TeamPlayerRead,
    create_schema=TeamPlayerCreate,
    update_schema=TeamPlayerUpdate,
    prefix="/team-players",
    tags=["Team Players"],
)
