from app.api.router_factory import build_crud_router
from app.crud.competition import season
from app.schemas.competition import SeasonCreate, SeasonRead, SeasonUpdate

router = build_crud_router(
    crud=season,
    read_schema=SeasonRead,
    create_schema=SeasonCreate,
    update_schema=SeasonUpdate,
    prefix="/seasons",
    tags=["Seasons"],
)
