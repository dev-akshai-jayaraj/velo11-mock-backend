from app.api.router_factory import build_crud_router
from app.crud.workflow import system_module
from app.schemas.workflow import SystemModuleCreate, SystemModuleRead, SystemModuleUpdate

router = build_crud_router(
    crud=system_module,
    read_schema=SystemModuleRead,
    create_schema=SystemModuleCreate,
    update_schema=SystemModuleUpdate,
    prefix="/system-modules",
    tags=["System Modules"],
)
