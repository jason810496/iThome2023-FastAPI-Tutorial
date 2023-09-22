from fastapi import APIRouter , Depends
from sqlalchemy import text

from setting.config import get_settings
from database.generic import get_db


router = APIRouter(
    tags=["infor"],
)


@router.get("/")
def hello_world():
    return "Hello World"

@router.get("/infor")
def get_infor():

    databases = None
    db_session = get_db()
    
    try :
        databases = db_session.execute(text("SELECT datname FROM pg_database;")).fetchall()
    except Exception as e:
        print(e)

    if databases is None:
        try :
            databases = db_session.execute(text("SHOW DATABASES;")).fetchall()
        except Exception as e:
            print(e)


    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "author": settings.author,
        "app_mode": settings.app_mode ,
        "port": settings.port,
        "reload": settings.reload,
        "db_type": settings.db_type,
        "database_url": settings.database_url,
        "database": str(databases)
    }