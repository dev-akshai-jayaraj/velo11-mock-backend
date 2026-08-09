from app.api.router_factory import build_crud_router
from app.crud.club import home_club
from app.schemas.club import HomeClubCreate, HomeClubRead, HomeClubUpdate

router = build_crud_router(
    crud=home_club,
    read_schema=HomeClubRead,
    create_schema=HomeClubCreate,
    update_schema=HomeClubUpdate,
    prefix="/home-clubs",
    tags=["Home Clubs"],
)
