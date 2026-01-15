from typing import List
from fastapi import APIRouter, Depends

from app.schemas.orders import OrderSchema, OrderCreate


from app.models.auth import User
from app.db.deps import get_current_user, PermissionChecker

router = APIRouter(prefix="/orders", tags=["orders"])


FAKE_DB_ORDERS = [
    {"id": 1, "item": "Macbook", "owner_email": "admin@example.com"},
    {"id": 2, "item": "Phone", "owner_email": "user@example.com"},
    {"id": 3, "item": "Monitor", "owner_email": "user@example.com"},
    {"id": 4, "item": "Headphones", "owner_email": "manager@example.com"},
]


@router.get("/", response_model=List[OrderSchema])
async def read_orders(
    user: User = Depends(get_current_user),
    has_access: bool = Depends(PermissionChecker(element_name="orders", action="read")),
):

    rule = next(r for r in user.role.rules if r.element.name == "orders")

    if rule.can_read_all:
        return FAKE_DB_ORDERS

    return [order for order in FAKE_DB_ORDERS if order["owner_email"] == user.email]


@router.post("/", response_model=OrderSchema)
async def create_order(
    order_in: OrderCreate,
    user: User = Depends(get_current_user),
    has_access: bool = Depends(
        PermissionChecker(element_name="orders", action="create")
    ),
):
    new_id = len(FAKE_DB_ORDERS) + 1
    new_order = {"id": new_id, "item": order_in.item, "owner_email": user.email}
    FAKE_DB_ORDERS.append(new_order)
    return new_order
