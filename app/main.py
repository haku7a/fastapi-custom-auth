from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.session import engine
from app.db.base_class import Base
from app.models import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"status": "ok", "message": "System is running"}
