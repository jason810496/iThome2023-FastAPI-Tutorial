from typing import Annotated

from fastapi import APIRouter, HTTPException, status 
from schemas.auth import login_form_schema, oauth2_token_scheme , Token , RefreshRequest
from auth.jwt import create_token_pair, verify_refresh_token

from jose import jwt , JWTError
from datetime import datetime , timedelta
from setting.config import get_settings


router = APIRouter(
    tags=["auth"],
    prefix="/api/auth",
)

settings = get_settings()


@router.post("/login",response_model=Token)
async def login(form_data: login_form_schema):
    """
    Login with the following information:

    - **username**
    - **password**

    """
    return await create_token_pair({"username": form_data.username},{"username": form_data.username})

@router.post("/refresh",response_model=Token)
async def refresh(refersh_data: RefreshRequest):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """

    payload : dict = await verify_refresh_token(refersh_data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username: str = payload.get("username")
    if username is None:
        raise  HTTPException(
            status_code=401,
            detail="Invalid token ( No `username` in payload )",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await create_token_pair({"username": username },{"username": username })
