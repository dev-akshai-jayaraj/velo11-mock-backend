from app.api.router_factory import build_crud_router
from app.crud.competition import competition
from app.schemas.competition import CompetitionCreate, CompetitionRead, CompetitionUpdate

router = build_crud_router(
    crud=competition,
    read_schema=CompetitionRead,
    create_schema=CompetitionCreate,
    update_schema=CompetitionUpdate,
    prefix="/competitions",
    tags=["Competitions"],
)
