from fastapi import APIRouter, HTTPException, status , Depends
from typing import List 

from schemas import users as UserSchema
from api.depends import check_user_id , pagination_parms
from crud.users import UserCrudManager

from auth.passwd import get_password_hash
from auth.jwt import verify_access_token
from auth.utils import get_current_user


router = APIRouter(
    tags=["users"],
    prefix="/api",
)

UserCrud = UserCrudManager()

Exception403 = HTTPException(status_code=403, detail="Permission denied")


@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
async def get_users(page_parms:dict= Depends(pagination_parms)):
    users = await UserCrud.get_users(**page_parms)
    return users

@router.get("/users/{user_id}" , response_model=UserSchema.UserRead )
async def get_user_infor_by_id(user_id: int):

    user = await UserCrud.get_user_infor_by_id(user_id=user_id)
    if user:
        return user
        
    raise HTTPException(status_code=404, detail="User not found")

@router.post("/users" ,
        response_model=UserSchema.UserCreateResponse,
        status_code=status.HTTP_201_CREATED,
        response_description="Create new user"
)
async def create_user(newUser: UserSchema.UserCreate ):
    """
    Create an user with the following information:

    - **name**
    - **password**
    - **age**
    - **birthday**
    - **email**
    - **avatar** (optional)

    """

    user = await UserCrud.get_user_id_by_email(email=newUser.email)
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")
    
    user = await UserCrud.create_user(newUser=newUser)
    return vars(user)

@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
async def update_user(
    newUser: UserSchema.UserUpdate,
    user_id:int=Depends(check_user_id),
    user:UserSchema.CurrentUser = Depends(get_current_user) ):
    
    if user.id != user_id:
        raise Exception403

    await UserCrud.update_user(newUser=newUser,user_id=user_id)
    return newUser

@router.put("/users/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_password(
    newUser:UserSchema.UserUpdatePassword,
    user_id:int=Depends(check_user_id),
    user:UserSchema.CurrentUser = Depends(get_current_user) ):

    if user.id != user_id:
        raise Exception403

    await UserCrud.update_user_password(newUser=newUser,user_id=user_id)
    return 



@router.post("/userCreate" , deprecated=True )
async def create_user_deprecated(newUser: UserSchema.UserCreate ):
    return "deprecated"

@router.delete("/users/{user_id}",status_code=status.HTTP_204_NO_CONTENT )
async def delete_users(
    user_id:int = Depends(check_user_id),
    user:UserSchema.CurrentUser = Depends(get_current_user) ):

    if user.id != user_id:
        raise Exception403

    await UserCrud.delete_user(user_id=user_id)
    return 
