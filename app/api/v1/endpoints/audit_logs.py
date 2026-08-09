from app.api.router_factory import build_crud_router
from app.crud.audit import audit_log
from app.schemas.audit import AuditLogCreate, AuditLogRead

router = build_crud_router(
    crud=audit_log,
    read_schema=AuditLogRead,
    create_schema=AuditLogCreate,
    update_schema=None,
    prefix="/audit-logs",
    tags=["Audit Logs"],
)
