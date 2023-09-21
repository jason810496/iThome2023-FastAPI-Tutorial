from fastapi import APIRouter, HTTPException, status
from typing import List , Dict

from schemas import users as UserSchema
from database.fake_db import get_db

fake_db = get_db()

router = APIRouter(
    tags=["users"],
    prefix="/api"
)

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(qry: str = None):
    """
    Create an user list with all the information:

    - **id**
    - **name**
    - **email**
    - **avatar**

    """
    return fake_db['users']

@router.get("/users/{user_id}" , response_model=UserSchema.UserRead )
def get_user_by_id(user_id: int, qry: str = None):

    for user in fake_db["users"]:
        if user["id"] == user_id:
            return user
        
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/users" ,
        response_model=UserSchema.UserCreateResponse,
        status_code=status.HTTP_201_CREATED,
        response_description="Create new user"
)
def create_users(newUser: UserSchema.UserCreate ):

    for user in fake_db["users"]:
        if user["id"] == newUser.id:
            raise HTTPException(status_code=409, detail="User already exists")
        
    fake_db["users"].routerend(newUser)
    return newUser

@router.post("/userCreate" , deprecated=True )
def create_user_deprecated(newUser: UserSchema.UserCreate ):
    return "deprecated"

@router.delete("/users/{user_id}" )
def delete_users(user_id: int):
    
    for user in fake_db["users"]:
        if user["id"] == user_id:
            fake_db["users"].remove(user)
            return user
        
    raise HTTPException(status_code=404, detail="User not found")