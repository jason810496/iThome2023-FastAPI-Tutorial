from fastapi import FastAPI

from setting.config import get_settings
from schemas.users import User as UserSchema
from schemas.items import Item as ItemSchema

fake_db = {
    "users": {
        1: {
            "name": "John",
            "age": 35,
            "email": "john@fakemail.com",
            "birthday": "2000-01-01",
        },
        2: {
            "name": "Jane",
            "age": 25,
            "email": "jane@fakemail.com",
            "birthday": "2010-12-04",
        }
    },
    "items": {
        1: {
            "name": "iPhone 12",
            "price": 1000,
            "brand": "Apple"
        },
        2: {
            "name": "Galaxy S21",
            "price": 800,
            "brand": "Samsung"
        }
    }
}

app = FastAPI()

@app.get("/")
def hello_world():
    return "Hello World"

@app.get("/infor")
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

@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    if user_id not in fake_db["users"]:
        return {"error": "User not found"}
    return {"user": fake_db['users'][user_id], "query": qry }

@app.post("/users")
def create_users(user: UserSchema):
    fake_db["users"][user.id] = user
    return user

@app.get("/items/{item_id}")
def get_items_without_typing(item_id, qry):
    if item_id not in fake_db["items"]:
        return {"error": "Item not found"}
    return {"item": fake_db['items'][item_id], "query": qry }

@app.post("/items")
def create_items(item: ItemSchema):
    fake_db["items"][item.id] = item
    return item