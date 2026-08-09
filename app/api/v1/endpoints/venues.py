from app.api.router_factory import build_crud_router
from app.crud.club import venue
from app.schemas.club import VenueCreate, VenueRead, VenueUpdate

router = build_crud_router(
    crud=venue,
    read_schema=VenueRead,
    create_schema=VenueCreate,
    update_schema=VenueUpdate,
    prefix="/venues",
    tags=["Venues"],
)
