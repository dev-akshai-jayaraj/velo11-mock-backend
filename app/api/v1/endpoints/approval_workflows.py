from app.api.router_factory import build_crud_router
from app.crud.workflow import approval_workflow
from app.schemas.workflow import (
    ApprovalWorkflowCreate,
    ApprovalWorkflowRead,
    ApprovalWorkflowUpdate,
)

router = build_crud_router(
    crud=approval_workflow,
    read_schema=ApprovalWorkflowRead,
    create_schema=ApprovalWorkflowCreate,
    update_schema=ApprovalWorkflowUpdate,
    prefix="/approval-workflows",
    tags=["Approval Workflows"],
)
