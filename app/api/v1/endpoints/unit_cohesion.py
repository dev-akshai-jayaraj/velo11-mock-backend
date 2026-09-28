from app.api.router_factory import build_crud_router
from app.crud.dynamics import unit_cohesion
from app.schemas.dynamics import UnitCohesionCreate, UnitCohesionRead, UnitCohesionUpdate

router = build_crud_router(
    crud=unit_cohesion,
    read_schema=UnitCohesionRead,
    create_schema=UnitCohesionCreate,
    update_schema=UnitCohesionUpdate,
    prefix="/unit-cohesion",
    tags=["Unit Cohesion"],
)
