from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import AsyncSessionFactory
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from app.models.auth import User, Role, AccessRule, TokenBlocklist
from app.core.security import decode_access_token
from sqlalchemy import select
from sqlalchemy.orm import selectinload

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionFactory() as session:
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    query_blocklist = select(TokenBlocklist).where(TokenBlocklist.token == token)
    result = await db.execute(query_blocklist)
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked (logged out)",
        )

    email = decode_access_token(token)
    if not email:
        raise credentials_exception

    query = (
        select(User)
        .options(
            selectinload(User.role)
            .selectinload(Role.rules)
            .selectinload(AccessRule.element)
        )
        .where(User.email == email)
    )

    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    return user


class PermissionChecker:
    def __init__(self, element_name: str, action: str):
        self.element_name = element_name
        self.action = action

    async def __call__(self, user: User = Depends(get_current_user)):
        if not user.role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no role assigned",
            )

        rule = next(
            (r for r in user.role.rules if r.element.name == self.element_name), None
        )

        if not rule:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"No access rules found for resource '{self.element_name}'",
            )

        has_permission = getattr(rule, f"can_{self.action}", False)

        if not has_permission:
            if self.action == "read" and rule.can_read_all:
                return True
            if self.action == "update" and rule.can_update_all:
                return True
            if self.action == "delete" and rule.can_delete_all:
                return True

            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You do not have permission to {self.action} this resource",
            )

        return True
