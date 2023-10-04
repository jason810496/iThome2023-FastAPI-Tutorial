# [Day18] OAuth2 實例： OAuth2 Schema & JWT

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day18 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day18)** <br>


## 回顧

我們在 [Day17](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day17) 完成密碼驗證的實作 <br>
今天會開始進入會來看如何使用 `fastapi.security` 中的 `OAuth2PasswordBearer` 來實作 **OAuth2 password login** <br>
和 **JWT token** 的實作 <br>

## OAuth2 Schema

如果要使用 `fastapi.security` 中的 `OAuth2PasswordBearer` <br>
需要加上 `python-multipart` 這個套件 <br>
```bash
poetry add python-multipart
```

<br>

我們就透過 `OAuth2PasswordRequestForm` 和 `OAuth2PasswordBearer` 這兩個 Schema <br>
來實作 OAuth2 password login <br>
並且也能在 Swagger UI 使用 `Authorize` 的按鈕 <br>
並顯示需要 token 才能使用的 API endpoint <br>

![swagger auth](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day18/swagger-auth.png)

<br>

## 新增 Authorize Endpoint 和 OAuth2 Schema

新增 `api/auth.py` <br>
並新增 Login 和 Refresh Endpoint
```python
from fastapi import APIRouter

router = APIRouter(
    tags=["auth"],
    prefix="/api/auth",
)


@router.post("/login")
async def login(form_da):
    """
    Login with the following information:

    - **username**
    - **password**

    """
    return {
        "access_token": "login_access_token",
        "refresh_token": "login_refresh_token",
        "token_type": "bearer",
    }

@router.post("/refresh",response_model=Token)
async def refresh(token: oauth2_token_scheme):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """
    return {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "bearer",
    }
```

<br>

新增 `schemas/auth.py` <br>
我們把 `OAuth2PasswordRequestForm` 和 `OAuth2PasswordBearer` 這兩個 Schema 都定義在 `schemas/auth.py` 中 <br>
並額外定義給 `response_model` 的 `LoginToken` 和 `Token` Schemas 

`schemas/auth.py`
```python
from typing import Annotated

from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer 

oauth2_token_scheme = Annotated[str,Depends(OAuth2PasswordBearer(tokenUrl="api/auth/login"))]
login_form_schema = Annotated[OAuth2PasswordRequestForm, Depends()]


class Token(BaseModel):
    access_token: str
    token_type: str

class RefreshRequest(BaseModel):
    refresh_token: str
```

<br>

比較特別的是 `oauth2_token_scheme` <br>
需要特別定義 `Depends()` 和 `tokenUrl` ( Login 的 Route )<br>
這樣才能在 Swagger UI 中使用 `Authorize` 的按鈕 <br>
而 `OAuth2PasswordBearer` 會檢查 `Authorization` header 中的 **Bearer token** <br>

<br>

接著就可以在 `api/auth.py` 中使用 `login_form_schema` 和 `oauth2_token_scheme` <br>
來將 Login 和 Refresh Endpoint 的 Schema 設定好 <br>

<br>

`api/auth.py`
```python
@router.post("/login",response_model=LoginToken)
async def login(form_data: login_form_schema):
    """
    Login with the following information:

    - **username**
    - **password**

    """
    return {
        "access_token": "login_access_token",
        "refresh_token": "login_refresh_token",
        "token_type": "bearer",
    }

@router.post("/refresh",response_model=RefreshRequest)
async def refresh(token: oauth2_token_scheme):
    """
    Refresh token with the following information:

    - **token** in `Authorization` header

    """
    return {
        "access_token": "new_access_token",
        "refresh_token": "new_refresh_token",
        "token_type": "bearer",
    }
```

<br>

就可以先來測試 Refresh Endpoint 是否需要帶入 token 才能使用 <br>



![swagger refresh error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day18/swagger-refresh-error.png)

不帶入 token 會回傳 401 Unauthorized <br>

<br>
 
![swagger refresh](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day18/swagger-refresh.png)
帶入後就可以拿到新的測試 token <br>

<br>

## 使用 JWT token

著著要來完成 JWT token 的實作 <br>
首先需要安裝 `python-jose` 這個套件 <br>
```bash
poetry add python-jose
```

### 設定 Secret Key 與 Token Expiration

在使用 JWT token 之前，我們需要先設定 Secret Key 和 Token Expiration <br>
要注意的是 `refresh_token` 的過期時間會設的比 `access_token` 長 <br>
並且兩個 token 的 Secret Key 也不一樣 <br>

<br>

`settings/.env.dev`
```bash
# ...

# for jwt

ACCESS_TOKEN_SECRET=YOUR_ACCESS_TOKEN_SECRET
ACCESS_TOKEN_EXPIRE_MINUTES=1

REFRESH_TOKEN_SECRET=YOUR_REFRESH_TOKEN_SECRET
REFRESH_TOKEN_EXPIRE_MINUTES=10
```

<br>

更新 `settings/config.py` <br>
```python
class Settins():
    # ...

    access_token_secret:str = os.getenv("ACCESS_TOKEN_SECRET")
    access_token_expire_minutes:int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    refresh_token_secret:str = os.getenv("REFRESH_TOKEN_SECRET")
    refresh_token_expire_minutes:int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES"))
```

### JWT Token

我們把 JWT token 的實作都放在 `auth/jwt.py` 中 <br>
首先需要先定義 `create_access_token` 和 `create_refresh_token` <br>
需要先 import `jwt` 和 `datetime` <br>
和載入 `settings` <br>

`auth/jwt.py`
```python
from datetime import datetime, timedelta
from jose import jwt

from setting.config import get_settings
from schemas.auth import Token

settings = get_settings()
```

<br>

透過 `python-jose` 的 `jwt.encode` 來產生 token <br>
而 `jwt.encode` 需要傳入一個 dict <br>
裡面可以放入我們想要的資訊 <br>
而 `expire` 會是過期時間，透過 `datetime.utcnow()` 來取得現在時間 <br>
再加上 `timedelta` 就會是過期時間 <br>

`auth/jwt.py`
```python
async def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.access_token_secret)
    return encoded_jwt
```

<br>

而 Refresh token 的實作也是一樣的 <br>
只是過期時間會設定比較長 <br>
再順便包裝成 `Token` Schema <br>

<br>

`auth/jwt.py`
```python
# ...
async def create_refresh_token(data: dict):   
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.refresh_token_expire_minutes)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.refresh_token_secret)
    return encoded_jwt

async def create_token_pair(access_data: dict,refresh_data:dict) -> Token:
    access_token = await create_access_token(access_data)
    refresh_token = await create_refresh_token(refresh_data)
    return Token(access_token=access_token,refresh_token=refresh_token,token_type="bearer")
```

## JWT Token Verification

我們可以透過 `jwt.decode` 來解碼 JWT token <br>
如果解碼失敗都會丟出 `JWTError` <br>
如果解碼成功會回傳一個 `dict` <br>
<br>

因為 token 過期會丟出 `ExpiredSignatureError` <br>
所以我們可以特別 catch 並 raise `HTTPException : Token expired` <br>

<br>

`auth/jwt.py`
```python
async def verify_refresh_token(token: str):
    try:
        payload = jwt.decode(token, settings.refresh_token_secret)
        return payload
    except ExpiredSignatureError:
        raise  HTTPException(
            status_code=401,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except JWTError:
        return None
```

<br>

接著就可以在 Refresh Endpoint 中使用 `verify_refresh_token` <br>
來檢查 JWT token 是否正確 <br>
如果正確就可以換發新的 token <br>

<br>

`api/auth.py`
```python

# ...
async def refresh(refersh_data: RefreshRequest):
    payload : dict = await verify_refresh_token(refersh_data.refresh_token)

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username: str = payload.get("user")
    if username is None:
        raise  HTTPException(
            status_code=401,
            detail="Invalid token ( No `username` in payload )",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # ...
```

<br>

如果我們拿一個過期的 refresh token 來測試 <br>
![expired token](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day18/expired-token.png)
就會回傳 401 Unauthorized ， 並且告知 Token expired <br>

<br>

以一個正確的 refresh token 來測試 <br>
![correct token](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day18/correct-token.png)
就可以拿到新的 access token 和 refresh token ! <br>

## 總結

今天我們學習了如何使用 `fastapi.security` 中的 `OAuth2PasswordBearer` 來實作 **OAuth2 password login** <br>




#### Reference

[FastAPI : OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)