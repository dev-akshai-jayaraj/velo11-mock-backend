from app.api.router_factory import build_crud_router
from app.crud.workflow import approval_action
from app.schemas.workflow import ApprovalActionCreate, ApprovalActionRead, ApprovalActionUpdate

router = build_crud_router(
    crud=approval_action,
    read_schema=ApprovalActionRead,
    create_schema=ApprovalActionCreate,
    update_schema=ApprovalActionUpdate,
    prefix="/approval-actions",
    tags=["Approval Actions"],
)
