from fastapi import APIRouter

from setting.config import get_settings

router = APIRouter(
    tags=["infor"],
)


@router.get("/")
def hello_world():
    return "Hello World"

@router.get("/infor")
def get_infor():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "author": settings.author,
        "app_mode": settings.app_mode ,
        "port": settings.port,
        "database_url": settings.database_url,
        "reload": settings.reload
    }