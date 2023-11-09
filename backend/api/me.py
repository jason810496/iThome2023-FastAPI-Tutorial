from fastapi import APIRouter, HTTPException, status , Depends

from schemas import users as UserSchema
from crud.users import UserCrudManager

from auth.utils import get_current_user


router = APIRouter(
    tags=["me"],
    prefix="/api/me",
)

UserCrud = UserCrudManager()

Exception403 = HTTPException(status_code=403, detail="Permission denied")


@router.get("" , response_model=UserSchema.UserInfor )
async def get_user_infor_by_id(
    user:UserSchema.CurrentUser = Depends(get_current_user) ):

    user = await UserCrud.get_user_infor_by_id(user_id=user.id)
    if user:
        return user
        
    raise HTTPException(status_code=404, detail="User not found")


@router.put("" , response_model=UserSchema.UserUpdateResponse )
async def update_user(
    newUser: UserSchema.UserUpdate,
    user:UserSchema.CurrentUser = Depends(get_current_user) ):
    
    if user.id != user.id:
        raise Exception403

    await UserCrud.update_user(newUser=newUser,user_id=user.id)
    return newUser

@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def update_user_password(
    newUser:UserSchema.UserUpdatePassword,
    user:UserSchema.CurrentUser = Depends(get_current_user) ):

    if user.id != user.id:
        raise Exception403

    await UserCrud.update_user_password(newUser=newUser,user_id=user.id)
    return 


@router.delete("",status_code=status.HTTP_204_NO_CONTENT )
async def delete_users(
    user:UserSchema.CurrentUser = Depends(get_current_user) ):

    if user.id != user.id:
        raise Exception403

    await UserCrud.delete_user(user_id=user.id)
    return 
