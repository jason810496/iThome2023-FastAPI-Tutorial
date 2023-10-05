from typing import Annotated

from fastapi import APIRouter, HTTPException, status 
from schemas.auth import login_form_schema, oauth2_token_scheme , Token , RefreshRequest
from auth.jwt import create_token_pair, verify_refresh_token
from auth.passwd import verify_password

from jose import jwt , JWTError
from datetime import datetime , timedelta
from setting.config import get_settings

from crud.users import UserCrudManager
from schemas.users import UserInDB


router = APIRouter(
    tags=["auth"],
    prefix="/api/auth",
)

settings = get_settings()

UserCrud = UserCrudManager()

exception_invalid_token = HTTPException(
    status_code=401,
    detail="Invalid token",
    headers={"WWW-Authenticate": "Bearer"}
)

exception_invalid_login = HTTPException(
    status_code=401,
    detail="Incorrect username or password",
    headers={"WWW-Authenticate": "Bearer"}
)


@router.post("/login",response_model=Token)
async def login(form_data: login_form_schema):
    """
    Login with the following information:

    - **username**
    - **password**

    """

    user_in_db:UserInDB = await UserCrud.get_user_in_db(form_data.username)

    if user_in_db is None:
        raise exception_invalid_login
    
    if not verify_password(form_data.password,user_in_db.password):
        raise exception_invalid_login
    
    return await create_token_pair(
        {"username": user_in_db.name, "id": user_in_db.id},
        {"username": user_in_db.name, "id": user_in_db.id},
    )

@router.post("/refresh",response_model=Token)
async def refresh(refersh_data: RefreshRequest):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """

    payload : dict = await verify_refresh_token(refersh_data.refresh_token)
    
    username: str = payload.get("username")
    u_id:int = payload.get("id")
    if username is None or u_id is None:
        raise  exception_invalid_token

    return await create_token_pair(
        {"username": username , "id": u_id},
        {"username": username , "id": u_id}
    )
