from pydantic import BaseModel, EmailStr


class AssignRoleSchema(BaseModel):
    user_email: EmailStr
    role_name: str


class UpdateRuleSchema(BaseModel):
    role_name: str
    element_name: str
    can_create: bool = False
    can_read: bool = False
    can_update: bool = False
    can_delete: bool = False
    can_read_all: bool = False
    can_update_all: bool = False
    can_delete_all: bool = False
