from fastapi import HTTPException , Depends

from crud.users import UserCrudManager
from schemas.auth import oauth2_token_scheme
from auth.jwt import verify_access_token
from schemas.users import CurrentUser

UserCrud = UserCrudManager()

async def get_current_user(token: oauth2_token_scheme )-> CurrentUser:
    payload = await verify_access_token(token)
    
    user_id = int(payload.get("id"))
    user = await UserCrud.get_user_by_id(user_id=user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user