from fastapi import FastAPI
from app.api.endpoints.auth import router as auth_router
from app.api.endpoints.orders import router as orders_router
from app.api.endpoints.admin import router as admin_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(orders_router)
app.include_router(admin_router)


@app.get("/")
async def read_root():
    return {"status": "ok", "message": "System is running"}
