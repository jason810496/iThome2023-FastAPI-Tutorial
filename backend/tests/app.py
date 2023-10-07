
import os 
from fastapi import FastAPI
from dotenv import load_dotenv

from setting.config import get_settings



settings = get_settings()

app = FastAPI()

from api.infor import router as infor_router
from api.users import router as user_router
from api.items import router as item_router
from api.auth import router as auth_router
from database.generic import init_db , close_db

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(item_router)
app.include_router(infor_router)

@app.on_event("startup")
async def startup():
    await init_db()

@app.on_event("shutdown")
async def shutdown():
    await close_db()