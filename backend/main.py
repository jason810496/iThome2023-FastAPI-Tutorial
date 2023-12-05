from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware
import sentry_sdk

from setting.config import get_settings

settings = get_settings()


if settings.sentry_dsn:
    sentry_sdk.init(
    dsn=settings.sentry_dsn,
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    # We recommend adjusting this value in production.
    profiles_sample_rate=1.0,
)

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

    

app = create_async_app()

