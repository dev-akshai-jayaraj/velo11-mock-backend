from app.api.router_factory import build_crud_router
from app.crud.preparation import opposition_analysis
from app.schemas.preparation import OppositionAnalysisCreate, OppositionAnalysisRead, OppositionAnalysisUpdate

router = build_crud_router(
    crud=opposition_analysis,
    read_schema=OppositionAnalysisRead,
    create_schema=OppositionAnalysisCreate,
    update_schema=OppositionAnalysisUpdate,
    prefix="/opposition-analyses",
    tags=["Opposition Analyses"],
)
