from app.api.router_factory import build_crud_router
from app.crud.insights import recommendation
from app.schemas.insights import RecommendationCreate, RecommendationRead, RecommendationUpdate

router = build_crud_router(
    crud=recommendation,
    read_schema=RecommendationRead,
    create_schema=RecommendationCreate,
    update_schema=RecommendationUpdate,
    prefix="/recommendations",
    tags=["Recommendations"],
)
