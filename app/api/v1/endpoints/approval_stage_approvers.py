from app.api.router_factory import build_crud_router
from app.crud.workflow import approval_stage_approver
from app.schemas.workflow import (
    ApprovalStageApproverCreate,
    ApprovalStageApproverRead,
    ApprovalStageApproverUpdate,
)

router = build_crud_router(
    crud=approval_stage_approver,
    read_schema=ApprovalStageApproverRead,
    create_schema=ApprovalStageApproverCreate,
    update_schema=ApprovalStageApproverUpdate,
    prefix="/approval-stage-approvers",
    tags=["Approval Stage Approvers"],
)
