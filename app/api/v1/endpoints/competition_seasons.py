from app.api.router_factory import build_crud_router
from app.crud.competition import competition_season
from app.schemas.competition import CompetitionSeasonCreate, CompetitionSeasonRead, CompetitionSeasonUpdate

router = build_crud_router(
    crud=competition_season,
    read_schema=CompetitionSeasonRead,
    create_schema=CompetitionSeasonCreate,
    update_schema=CompetitionSeasonUpdate,
    prefix="/competition-seasons",
    tags=["Competition Seasons"],
)
