from app.api.router_factory import build_crud_router
from app.crud.workflow import approval_request
from app.schemas.workflow import (
    ApprovalRequestCreate,
    ApprovalRequestRead,
    ApprovalRequestUpdate,
)

router = build_crud_router(
    crud=approval_request,
    read_schema=ApprovalRequestRead,
    create_schema=ApprovalRequestCreate,
    update_schema=ApprovalRequestUpdate,
    prefix="/approval-requests",
    tags=["Approval Requests"],
)
