from fastapi import FastAPI 

from api.infor import router as infor_router
from api.users import router as user_router
from api.items import router as item_router

app = FastAPI()

app.include_router(infor_router)
app.include_router(user_router)
app.include_router(item_router)


