from app.api.router_factory import build_crud_router
from app.crud.user import role
from app.schemas.user import RoleCreate, RoleRead, RoleUpdate

router = build_crud_router(
    crud=role,
    read_schema=RoleRead,
    create_schema=RoleCreate,
    update_schema=RoleUpdate,
    prefix="/roles",
    tags=["Roles"],
)
