from app.api.router_factory import build_crud_router
from app.crud.match import fixture
from app.schemas.match import FixtureCreate, FixtureRead, FixtureUpdate

router = build_crud_router(
    crud=fixture,
    read_schema=FixtureRead,
    create_schema=FixtureCreate,
    update_schema=FixtureUpdate,
    prefix="/fixtures",
    tags=["Fixtures"],
)
