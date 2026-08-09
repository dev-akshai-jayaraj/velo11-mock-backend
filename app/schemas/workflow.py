import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SystemModuleBase(BaseModel):
    name: str
    code: str
    description: str | None = None
    is_active: bool = True


class SystemModuleCreate(SystemModuleBase):
    pass


class SystemModuleUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    is_active: bool | None = None


class SystemModuleRead(SystemModuleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ApprovalWorkflowBase(BaseModel):
    module_id: uuid.UUID
    name: str
    code: str
    is_required: bool = False
    is_active: bool = True


class ApprovalWorkflowCreate(ApprovalWorkflowBase):
    pass


class ApprovalWorkflowUpdate(BaseModel):
    module_id: uuid.UUID | None = None
    name: str | None = None
    code: str | None = None
    is_required: bool | None = None
    is_active: bool | None = None


class ApprovalWorkflowRead(ApprovalWorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ApprovalStageBase(BaseModel):
    workflow_id: uuid.UUID
    name: str
    stage_order: int
    approval_type: str = "ANY"
    is_final_stage: bool = False


class ApprovalStageCreate(ApprovalStageBase):
    pass


class ApprovalStageUpdate(BaseModel):
    workflow_id: uuid.UUID | None = None
    name: str | None = None
    stage_order: int | None = None
    approval_type: str | None = None
    is_final_stage: bool | None = None


class ApprovalStageRead(ApprovalStageBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ApprovalStageApproverBase(BaseModel):
    approval_stage_id: uuid.UUID
    role_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    approver_type: str = "ROLE"


class ApprovalStageApproverCreate(ApprovalStageApproverBase):
    pass


class ApprovalStageApproverUpdate(BaseModel):
    approval_stage_id: uuid.UUID | None = None
    role_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    approver_type: str | None = None


class ApprovalStageApproverRead(ApprovalStageApproverBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ApprovalRequestBase(BaseModel):
    workflow_id: uuid.UUID
    module_id: uuid.UUID
    record_id: uuid.UUID
    record_type: str
    current_status: str = "SUBMITTED"
    current_stage_order: int | None = None
    submitted_by: uuid.UUID
    submitted_at: datetime | None = None
    completed_at: datetime | None = None


class ApprovalRequestCreate(ApprovalRequestBase):
    pass


class ApprovalRequestUpdate(BaseModel):
    workflow_id: uuid.UUID | None = None
    module_id: uuid.UUID | None = None
    record_id: uuid.UUID | None = None
    record_type: str | None = None
    current_status: str | None = None
    current_stage_order: int | None = None
    submitted_by: uuid.UUID | None = None
    submitted_at: datetime | None = None
    completed_at: datetime | None = None


class ApprovalRequestRead(ApprovalRequestBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ApprovalActionBase(BaseModel):
    approval_request_id: uuid.UUID
    approval_stage_id: uuid.UUID | None = None
    action_by: uuid.UUID
    action: str
    comments: str | None = None
    action_at: datetime


class ApprovalActionCreate(ApprovalActionBase):
    pass


class ApprovalActionUpdate(BaseModel):
    approval_request_id: uuid.UUID | None = None
    approval_stage_id: uuid.UUID | None = None
    action_by: uuid.UUID | None = None
    action: str | None = None
    comments: str | None = None
    action_at: datetime | None = None


class ApprovalActionRead(ApprovalActionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
