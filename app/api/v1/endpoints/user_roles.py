from app.api.router_factory import build_crud_router
from app.crud.user import user_role
from app.schemas.user import UserRoleCreate, UserRoleRead, UserRoleUpdate

router = build_crud_router(
    crud=user_role,
    read_schema=UserRoleRead,
    create_schema=UserRoleCreate,
    update_schema=UserRoleUpdate,
    prefix="/user-roles",
    tags=["User Roles"],
)
