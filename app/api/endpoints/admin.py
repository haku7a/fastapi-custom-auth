from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.deps import get_db, PermissionChecker
from app.models.auth import User, Role, AccessRule, BusinessElement
from app.schemas.admin import AssignRoleSchema, UpdateRuleSchema

router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/assign-role")
async def assign_role_to_user(
    data: AssignRoleSchema,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(
        PermissionChecker(element_name="access_control", action="update")
    ),
):

    user = (
        await db.execute(select(User).where(User.email == data.user_email))
    ).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    role = (
        await db.execute(select(Role).where(Role.name == data.role_name))
    ).scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    user.role_id = role.id
    await db.commit()

    return {"message": f"Role '{data.role_name}' assigned to user '{data.user_email}'"}


@router.post("/update-rules")
async def update_access_rule(
    data: UpdateRuleSchema,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(
        PermissionChecker(element_name="access_control", action="update")
    ),
):

    role = (
        await db.execute(select(Role).where(Role.name == data.role_name))
    ).scalar_one_or_none()
    element = (
        await db.execute(
            select(BusinessElement).where(BusinessElement.name == data.element_name)
        )
    ).scalar_one_or_none()

    if not role or not element:
        raise HTTPException(
            status_code=404, detail="Role or Business Element not found"
        )

    query = select(AccessRule).where(
        AccessRule.role_id == role.id, AccessRule.element_id == element.id
    )
    rule = (await db.execute(query)).scalar_one_or_none()

    if not rule:
        rule = AccessRule(role_id=role.id, element_id=element.id)
        db.add(rule)

    rule.can_create = data.can_create
    rule.can_read = data.can_read
    rule.can_update = data.can_update
    rule.can_delete = data.can_delete
    rule.can_read_all = data.can_read_all
    rule.can_update_all = data.can_update_all
    rule.can_delete_all = data.can_delete_all

    await db.commit()
    return {
        "message": f"Access rules updated for Role '{role.name}' on '{element.name}'"
    }
