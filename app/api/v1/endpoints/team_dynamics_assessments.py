from app.api.router_factory import build_crud_router
from app.crud.dynamics import team_dynamics_assessment
from app.schemas.dynamics import TeamDynamicsAssessmentCreate, TeamDynamicsAssessmentRead, TeamDynamicsAssessmentUpdate

router = build_crud_router(
    crud=team_dynamics_assessment,
    read_schema=TeamDynamicsAssessmentRead,
    create_schema=TeamDynamicsAssessmentCreate,
    update_schema=TeamDynamicsAssessmentUpdate,
    prefix="/team-dynamics-assessments",
    tags=["Team Dynamics Assessments"],
)
