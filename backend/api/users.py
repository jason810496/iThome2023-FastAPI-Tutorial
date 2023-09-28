from fastapi import APIRouter, HTTPException, status , Depends
from typing import List , Annotated
from pydantic import Field
from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete

from schemas import users as UserSchema
from database.generic import get_db
from models.user import User as UserModel 

from api.depends import check_user_id , pagination_parms, test_verify_token


router = APIRouter(
    tags=["users"],
    prefix="/api",
)

db_session:Session = get_db()

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(page_parms= Depends(pagination_parms)):

    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
    users = db_session.execute(stmt).all()

    return users

@router.get("/users/{user_id}" , response_model=UserSchema.UserRead )
def get_user_by_id(user_id: int, qry: str = None):

    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()
    if user:
        return user
        
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/users" ,
        response_model=UserSchema.UserCreateResponse,
        status_code=status.HTTP_201_CREATED,
        response_description="Create new user"
)
def create_user(newUser: UserSchema.UserCreate ):
    """
    Create an user with the following information:

    - **name**
    - **password**
    - **age**
    - **birthday**
    - **email**
    - **avatar** (optional)

    """

    stmt = select(UserModel.id).where(UserModel.email == newUser.email)
    user = db_session.execute(stmt).first()
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")
    
    # create user
    user = UserModel(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        email=newUser.email,
        avatar=newUser.avatar
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return vars(user)

@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
def update_user(newUser: UserSchema.UserUpdate,user_id:int=Depends(check_user_id) ):
    
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        avatar=newUser.avatar
    )

    db_session.execute(stmt)
    db_session.commit()

    return newUser

@router.put("/users/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
def update_user_password(newUser:UserSchema.UserUpdatePassword,user_id:int=Depends(check_user_id)):
    
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        password=newUser.password,
    )

    db_session.execute(stmt)
    db_session.commit()

    return 



@router.post("/userCreate" , deprecated=True )
def create_user_deprecated(newUser: UserSchema.UserCreate ):
    return "deprecated"

@router.delete("/users/{user_id}",status_code=status.HTTP_204_NO_CONTENT )
def delete_users(user_id:int = Depends(check_user_id) ):
    
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db_session.execute(stmt)
    db_session.commit()

    return 
