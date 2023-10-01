from fastapi import APIRouter, HTTPException, status , Depends
from typing import List 
from sqlalchemy.ext.asyncio import AsyncSession

from schemas import users as UserSchema
from api.depends import check_user_id , pagination_parms
from crud import users as UserCrud
from crud.users import UserCrudManager , get_user_crud_manager
from database.generic import get_db


router = APIRouter(
    tags=["users"],
    prefix="/api",
)

# db_depends:AsyncSession = Depends(get_user_crud_manager)
# db_depends = UserCrudManager()

userCrud = UserCrudManager()




# @router.get("/users", 
#         response_model=List[UserSchema.UserRead],
#         response_description="Get list of user",  
# )
# async def get_users(page_parms:dict= Depends(pagination_parms),db_session:AsyncSession=db_depends):
#     users = await UserCrud.get_users(db_session,**page_parms)
#     return users

# UserCRUD = UserCrudManager(Depends(get_db))

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
async def get_users(page_parms:dict= Depends(pagination_parms)):
    # users = await UserCrud.get_users(**page_parms)
    users = await userCrud.get_users(**page_parms)
    return users

@router.get("/users/{user_id}" , response_model=UserSchema.UserRead )
def get_user_by_id(user_id: int):

    user = UserCrud.get_user_by_id(user_id)
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

    user = UserCrud.get_user_id_by_email(newUser.email)
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")
    
    user = UserCrud.create_user(newUser)
    return vars(user)

@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
def update_user(newUser: UserSchema.UserUpdate,user_id:int=Depends(check_user_id) ):
    
    UserCrud.update_user(newUser,user_id)
    return newUser

@router.put("/users/{user_id}/password", status_code=status.HTTP_204_NO_CONTENT)
def update_user_password(newUser:UserSchema.UserUpdatePassword,user_id:int=Depends(check_user_id)):

    UserCrud.update_user_password(newUser,user_id)
    return 



@router.post("/userCreate" , deprecated=True )
def create_user_deprecated(newUser: UserSchema.UserCreate ):
    return "deprecated"

@router.delete("/users/{user_id}",status_code=status.HTTP_204_NO_CONTENT )
def delete_users(user_id:int = Depends(check_user_id) ):

    UserCrud.delete_user(user_id)
    return 
