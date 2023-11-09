from fastapi import APIRouter
from sqlalchemy import text

from setting.config import get_settings
from database.primary_replica import get_write_db as get_db
from models.user import User
from models.item import Item


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

@router.get("/test/create")
def test():
    db_session = get_db()
    result = {
        "user": None,
        "item": None,
    }
    try :

        test_user = User("123456", "test0", 0, None, "2000-01-01", "123@email.com")
        db_session.add(test_user)
        db_session.commit()
        result["user"] = str(test_user)

        test_item = Item("item0",99.9, "brand0", "test0", test_user.id)
        db_session.add(test_item)
        db_session.commit()
        result["item"] = str(test_item)

    except Exception as e:
        print(e)

    return result

@router.get("/test/read")
def test():
    db_session = get_db()
    result = {
        "user": None,
        "item": None,
        "user.items": None,
    }
    try :

        test_user = db_session.query(User).filter(User.name == "test0").first()
        result["user"] = test_user

        test_item = db_session.query(Item).filter(Item.brand == "brand0").first()
        result["item"] = test_item

        result["user.items"] = test_user.items
        

        

    except Exception as e:
        print(e)

    return result