from app.api.router_factory import build_crud_router
from app.crud.insights import report
from app.schemas.insights import ReportCreate, ReportRead, ReportUpdate

router = build_crud_router(
    crud=report,
    read_schema=ReportRead,
    create_schema=ReportCreate,
    update_schema=ReportUpdate,
    prefix="/reports",
    tags=["Reports"],
)
