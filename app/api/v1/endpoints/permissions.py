from app.api.router_factory import build_crud_router
from app.crud.user import permission
from app.schemas.user import PermissionCreate, PermissionRead, PermissionUpdate

router = build_crud_router(
    crud=permission,
    read_schema=PermissionRead,
    create_schema=PermissionCreate,
    update_schema=PermissionUpdate,
    prefix="/permissions",
    tags=["Permissions"],
)
