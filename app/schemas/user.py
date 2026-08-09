import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    home_club_id: uuid.UUID
    first_name: str
    last_name: str | None = None
    email: EmailStr
    phone: str | None = None
    status: str = "ACTIVE"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    home_club_id: uuid.UUID | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
    phone: str | None = None
    status: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_login_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RoleBase(BaseModel):
    name: str
    code: str
    description: str | None = None
    is_system_role: bool = False


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: str | None = None
    code: str | None = None
    description: str | None = None
    is_system_role: bool | None = None


class RoleRead(RoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class PermissionBase(BaseModel):
    module_code: str
    action_code: str
    name: str
    description: str | None = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    module_code: str | None = None
    action_code: str | None = None
    name: str | None = None
    description: str | None = None


class PermissionRead(PermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserRoleBase(BaseModel):
    user_id: uuid.UUID
    role_id: uuid.UUID
    assigned_by: uuid.UUID | None = None


class UserRoleCreate(UserRoleBase):
    pass


class UserRoleUpdate(BaseModel):
    user_id: uuid.UUID | None = None
    role_id: uuid.UUID | None = None
    assigned_by: uuid.UUID | None = None


class UserRoleRead(UserRoleBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    assigned_at: datetime


class RolePermissionBase(BaseModel):
    role_id: uuid.UUID
    permission_id: uuid.UUID


class RolePermissionCreate(RolePermissionBase):
    pass


class RolePermissionUpdate(BaseModel):
    role_id: uuid.UUID | None = None
    permission_id: uuid.UUID | None = None


class RolePermissionRead(RolePermissionBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: datetime
