from app.api.router_factory import build_crud_router
from app.crud.preparation import tactical_plan
from app.schemas.preparation import TacticalPlanCreate, TacticalPlanRead, TacticalPlanUpdate

router = build_crud_router(
    crud=tactical_plan,
    read_schema=TacticalPlanRead,
    create_schema=TacticalPlanCreate,
    update_schema=TacticalPlanUpdate,
    prefix="/tactical-plans",
    tags=["Tactical Plans"],
)
