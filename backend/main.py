from fastapi import FastAPI , HTTPException

from typing import List , Dict

from setting.config import get_settings
from schemas import users as UserSchema
from schemas import items as ItemSchema
from database.fake_db import get_db

app = FastAPI()

fake_db : List[Dict[str,str]]= get_db()

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

@app.get("/users", response_model=List[UserSchema.UserRead])
def get_users(qry: str = None):
    return fake_db['users']

@app.get("/users/{user_id}" , response_model=UserSchema.UserRead )
def get_user_by_id(user_id: int, qry: str = None):

    for user in fake_db["users"]:
        if user["id"] == user_id:
            return user
        
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/users" , response_model=UserSchema.UserCreateResponse )
def create_users(newUser: UserSchema.UserCreate ):

    for user in fake_db["users"]:
        if user["id"] == newUser.id:
            raise HTTPException(status_code=409, detail="User already exists")
        
    fake_db["users"].append(newUser)
    return newUser

@app.delete("/users/{user_id}" )
def delete_users(user_id: int):
    
    for user in fake_db["users"]:
        if user["id"] == user_id:
            fake_db["users"].remove(user)
            return user
        
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/items" , response_model=List[ItemSchema.ItemRead])
def get_items(qry: str = None):
    return fake_db['items']

@app.get("/items/{item_id}" , response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id : int , qry : str = None ):

    for item in fake_db["users"]:
        if item["id"] == item_id:
            return item
        
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/items" , response_model=ItemSchema.ItemCreate)
def create_items(newItem: ItemSchema.ItemCreate ):

    for item in fake_db["items"]:
        if item["id"] == newItem.id:
            raise HTTPException(status_code=409, detail="Item already exists")
        
    fake_db["items"].append(newItem)
    return newItem

@app.delete("/items/{item_id}")
def delete_items(item_id: int):
        
    for item in fake_db["items"]:
        if item["id"] == item_id:
            fake_db["items"].remove(item)
            return item
        
    raise HTTPException(status_code=404, detail="Item not found")
