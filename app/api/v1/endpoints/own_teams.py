from app.api.router_factory import build_crud_router
from app.crud.club import own_team
from app.schemas.club import OwnTeamCreate, OwnTeamRead, OwnTeamUpdate

router = build_crud_router(
    crud=own_team,
    read_schema=OwnTeamRead,
    create_schema=OwnTeamCreate,
    update_schema=OwnTeamUpdate,
    prefix="/own-teams",
    tags=["Own Teams"],
)
