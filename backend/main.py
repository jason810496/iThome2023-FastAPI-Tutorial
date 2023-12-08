from fastapi import FastAPI , Request
from fastapi.middleware.cors import CORSMiddleware
import time
import logging

from setting.config import get_settings

settings = get_settings()


origins = [
    "http://localhost:8001",
    "http://localhost:5000",
    "http://localhost:5137", # for frontend
]

def create_async_app():
    from api.infor import router as infor_router
    from api.users import router as user_router
    from api.items import router as item_router
    from api.auth import router as auth_router
    from api.me import router as me_router
    from database.injection import init_db , close_db

    app = FastAPI()

    app.include_router(auth_router)
    app.include_router(user_router)
    app.include_router(me_router)
    app.include_router(item_router)
    app.include_router(infor_router)

    @app.on_event("startup")
    async def startup():
        print("startup")
        await init_db()

    @app.on_event("shutdown")
    async def shutdown():
        await close_db()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app
    
def create_sync_app():
    from sync.api.infor import router as infor_router
    from sync.api.users import router as user_router
    from sync.api.items import router as item_router
    from sync.database.generic import init_db , close_db

    app = FastAPI()

    app.include_router(infor_router)
    app.include_router(user_router)
    app.include_router(item_router)
    

    @app.on_event("startup")
    def startup():
        init_db()

    @app.on_event("shutdown")
    def shutdown():
        close_db()
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

def create_message_queue_app():

    app = FastAPI()

    logger = logging.getLogger("uvicorn")
    logger.setLevel(logging.DEBUG)

    @app.on_event("startup")
    async def startup():
        logger.info("API Server is starting...")

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: callable):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time)
        formatted_process_time = '{0:.4f}'.format(process_time)
        logger.info(f"{request.method} {request.url} {formatted_process_time}s")
        response.headers["X-Process-Time"] = formatted_process_time

        return response

    from api.stt import router as stt_router

    app.include_router(stt_router)

    

    return app

    

# app = create_async_app()

mq_app = create_message_queue_app()

