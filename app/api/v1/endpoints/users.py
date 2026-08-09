from app.api.router_factory import build_crud_router
from app.crud.user import user
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = build_crud_router(
    crud=user,
    read_schema=UserRead,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    prefix="/users",
    tags=["Users"],
)
