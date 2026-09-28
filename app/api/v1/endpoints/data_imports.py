from app.api.router_factory import build_crud_router
from app.crud.ingestion import data_import
from app.schemas.ingestion import DataImportCreate, DataImportRead, DataImportUpdate

router = build_crud_router(
    crud=data_import,
    read_schema=DataImportRead,
    create_schema=DataImportCreate,
    update_schema=DataImportUpdate,
    prefix="/data-imports",
    tags=["Data Imports"],
)
