import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin, UUIDPkMixin


class SystemModule(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "system_modules"

    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ApprovalWorkflow(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "approval_workflows"
    __table_args__ = (UniqueConstraint("module_id", "code"),)

    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("system_modules.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ApprovalStage(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "approval_stages"
    __table_args__ = (UniqueConstraint("workflow_id", "stage_order"),)

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflows.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    stage_order: Mapped[int] = mapped_column(Integer, nullable=False)
    approval_type: Mapped[str] = mapped_column(String, nullable=False, default="ANY")
    is_final_stage: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)


class ApprovalStageApprover(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "approval_stage_approvers"

    approval_stage_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_stages.id"), nullable=False
    )
    role_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("roles.id")
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id")
    )
    approver_type: Mapped[str] = mapped_column(String, nullable=False, default="ROLE")


class ApprovalRequest(Base, UUIDPkMixin, TimestampMixin):
    __tablename__ = "approval_requests"

    workflow_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_workflows.id"), nullable=False
    )
    module_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("system_modules.id"), nullable=False
    )
    record_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    record_type: Mapped[str] = mapped_column(String, nullable=False)
    current_status: Mapped[str] = mapped_column(String, nullable=False, default="SUBMITTED")
    current_stage_order: Mapped[int | None] = mapped_column(Integer)
    submitted_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    submitted_at: Mapped[datetime | None] = mapped_column(DateTime)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime)


class ApprovalAction(Base, UUIDPkMixin):
    __tablename__ = "approval_actions"

    approval_request_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_requests.id"), nullable=False
    )
    approval_stage_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("approval_stages.id")
    )
    action_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    action: Mapped[str] = mapped_column(String, nullable=False)
    comments: Mapped[str | None] = mapped_column(Text)
    action_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
