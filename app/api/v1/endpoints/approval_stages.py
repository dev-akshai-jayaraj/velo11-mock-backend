from app.api.router_factory import build_crud_router
from app.crud.workflow import approval_stage
from app.schemas.workflow import ApprovalStageCreate, ApprovalStageRead, ApprovalStageUpdate

router = build_crud_router(
    crud=approval_stage,
    read_schema=ApprovalStageRead,
    create_schema=ApprovalStageCreate,
    update_schema=ApprovalStageUpdate,
    prefix="/approval-stages",
    tags=["Approval Stages"],
)
