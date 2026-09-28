from app.api.router_factory import build_crud_router
from app.crud.ingestion import data_source
from app.schemas.ingestion import DataSourceCreate, DataSourceRead, DataSourceUpdate

router = build_crud_router(
    crud=data_source,
    read_schema=DataSourceRead,
    create_schema=DataSourceCreate,
    update_schema=DataSourceUpdate,
    prefix="/data-sources",
    tags=["Data Sources"],
)
