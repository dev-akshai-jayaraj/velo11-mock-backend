from app.api.router_factory import build_crud_router
from app.crud.user import role_permission
from app.schemas.user import RolePermissionCreate, RolePermissionRead, RolePermissionUpdate

router = build_crud_router(
    crud=role_permission,
    read_schema=RolePermissionRead,
    create_schema=RolePermissionCreate,
    update_schema=RolePermissionUpdate,
    prefix="/role-permissions",
    tags=["Role Permissions"],
)
