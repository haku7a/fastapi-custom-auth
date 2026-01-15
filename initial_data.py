import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionFactory
from app.models.auth import Role, BusinessElement, AccessRule, User
from app.core.security import get_password_hash


async def init_db():
    async with AsyncSessionFactory() as session:
        elements_list = ["orders", "access_control"]
        db_elements = {}

        for name in elements_list:
            stmt = select(BusinessElement).where(BusinessElement.name == name)
            obj = (await session.execute(stmt)).scalar_one_or_none()
            if not obj:
                obj = BusinessElement(name=name)
                session.add(obj)
                print(f"Created Element: {name}")
            db_elements[name] = obj

        roles_list = ["admin", "user"]
        db_roles = {}

        for name in roles_list:
            stmt = select(Role).where(Role.name == name)
            obj = (await session.execute(stmt)).scalar_one_or_none()
            if not obj:
                obj = Role(name=name)
                session.add(obj)
                print(f"Created Role: {name}")
            db_roles[name] = obj

        await session.commit()

        for el in db_elements.values():
            await session.refresh(el)
        for rl in db_roles.values():
            await session.refresh(rl)

        for el_name, el_obj in db_elements.items():
            stmt = select(AccessRule).where(
                AccessRule.role_id == db_roles["admin"].id,
                AccessRule.element_id == el_obj.id,
            )
            if not (await session.execute(stmt)).scalar_one_or_none():
                session.add(
                    AccessRule(
                        role_id=db_roles["admin"].id,
                        element_id=el_obj.id,
                        can_create=True,
                        can_read=True,
                        can_update=True,
                        can_delete=True,
                        can_read_all=True,
                        can_update_all=True,
                        can_delete_all=True,
                    )
                )

        stmt = select(AccessRule).where(
            AccessRule.role_id == db_roles["user"].id,
            AccessRule.element_id == db_elements["orders"].id,
        )
        if not (await session.execute(stmt)).scalar_one_or_none():
            session.add(
                AccessRule(
                    role_id=db_roles["user"].id,
                    element_id=db_elements["orders"].id,
                    can_create=True,
                    can_read=True,
                    can_update=False,
                    can_delete=False,
                    can_read_all=False,
                    can_update_all=False,
                    can_delete_all=False,
                )
            )

        admin_email = "admin@example.com"
        stmt = select(User).where(User.email == admin_email)
        if not (await session.execute(stmt)).scalar_one_or_none():
            admin = User(
                full_name="Super Admin",
                email=admin_email,
                hashed_password=get_password_hash("admin123"),
                role_id=db_roles["admin"].id,
                is_active=True,
            )
            session.add(admin)

        user_email = "user@example.com"
        stmt = select(User).where(User.email == user_email)
        if not (await session.execute(stmt)).scalar_one_or_none():
            regular_user = User(
                full_name="Regular User",
                email=user_email,
                hashed_password=get_password_hash("user123"),
                role_id=db_roles["user"].id,
                is_active=True,
            )
            session.add(regular_user)

        await session.commit()


if __name__ == "__main__":
    asyncio.run(init_db())
