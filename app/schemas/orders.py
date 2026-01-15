from pydantic import BaseModel


class OrderSchema(BaseModel):
    id: int
    item: str
    owner_email: str


class OrderCreate(BaseModel):
    item: str
