from app.api.router_factory import build_crud_router
from app.crud.insights import analytics_snapshot
from app.schemas.insights import AnalyticsSnapshotCreate, AnalyticsSnapshotRead

router = build_crud_router(
    crud=analytics_snapshot,
    read_schema=AnalyticsSnapshotRead,
    create_schema=AnalyticsSnapshotCreate,
    update_schema=None,
    prefix="/analytics-snapshots",
    tags=["Analytics Snapshots"],
)
