# [Day19] OAuth2 實例：Authorize Dependency 、 權限管理

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day19 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day19)** <br>

## 回顧

我們在 [Day17](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day17) 完成 hash password 的實作 <br>
在 [Day18](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day18) 完成 JWT token 的實作 <br>

今天我們會完成整體 OAuth2 password login 的實作 <br>
包括 **Authorize Dependency** 和 **權限管理** <br>

## OAuth2 Login 實作

因為我們在註冊 User 時，都是以 Email 作為 username <br>
所以在 Login 時，也要以 Email 作為 username <br>

<br>

並且我們需要在 `crud/user.py` 中新增 `get_user_in_db` <br>
讓我們只取出 `User` 中的 `username` 和 `password` <br>

`crud/user.py`
```python
#  ...
class UserCrudManager:
    # ...
    async def get_user_in_db(self,email: str,db_session:AsyncSession=None) -> UserSchema.UserInDB :
        stmt = select(UserModel.id,UserModel.name,UserModel.password).where(UserModel.email == email)
        result = await db_session.execute(stmt)
        user = result.first()
        if user:
            return user
            
        return None
# ...
```

<br>

也可以順便加上 `UserInDB` 的 schema <br>
讓我們在 API Endpoint 知道 `get_user_in_db` 回傳的資料格式 <br>

`schemas/user.py`
```python

# ...

class UserInDB(BaseModel):
    id: int
    name: str
    password: str
```

<br>

接著我們就可以在 `api/auth.py` 中實作 Login Endpoint <br>
先透過 `get_user_in_db` 取得 `User` 的 `username` 和 `password` <br>
如果沒有該 `User`，就先丟出 `HTTPException` <br>

`api/auth.py`
```python

@router.post("/login",response_model=Token)
async def login(form_data: login_form_schema):

    user_in_db:UserInDB = await UserCrud.get_user_in_db(form_data.username)

    if user_in_db is None:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # ...
```

<br>

再接著檢查密碼是否正確 <br>
如果也沒問題，就回傳一組新的 JWT token <br>

`api/auth.py`
```python
async def login(form_data: login_form_schema):
    # ...

    if not verify_password(form_data.password,user_in_db.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return await create_token_pair({"username": user_in_db.name},{"username": user_in_db.name})
```

### 測試 Login Endpoint

先創建一個測試 User <br>

![create user](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/create-user.png)

<br>

以正確的帳號密碼來測試 <br>
![correct login](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/correct-login.png)

<br>

以錯誤密碼來測試 <br>
![incorrect password](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/incorrect-password.png)

<br>

以錯誤帳號來測試 <br>

![incorrect username](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/incorrect-username.png)

<br>

## Authorize Dependency

針對一些需要登入才能使用的 API Endpoint <br>
我們應該要帶入 JWT token 來驗證使用者身份 <br>

<br>

這邊我們使用 `fastapi.security` 中的 `OAuth2PasswordBearer` <br>
來作為 Authorize Dependency <br>
這邊先以 `update_user` API Endpoint 為例 <br>

<br>

`api/user.py`
```python
@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
async def update_user(
    newUser: UserSchema.UserUpdate,
    user_id:int=Depends(check_user_id),
    token:str = Depends(OAuth2PasswordBearer(tokenUrl="api/auth/login")) # <----- 新增
    ):
    # ...
```

<br>

在 Swagger UI 中，我們可以看到 `update_user` API Endpoint 被加上了鎖頭 <br>
![lock](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/lock.png)

並且我們按下鎖頭後，就可以輸入 Username 和 Password <br>
Swagger UI 會幫我們帶入 `tokenUrl` 中的 URL <br>
並在 `Authorization` header 中帶入 JWT token <br>

![authorize](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/authorize.png)

<br>

當我們輸入正確的帳號密碼後，就可以成功打 `update_user` API Endpoint <br>
![update user](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/update-user.png)

<br>

### 權限管理

但我們還遇到一個**嚴重的問題** <br>
就是**任何有登入的 User**都可以使用 `update_user` API Endpoint <br>

<br>

所以我們應該要在 `update_user` API Endpoint 中檢查 JWT token 中的 User 與 `user_id` 是否相同 <br>
又因為我們的 `User.name` 可以重複 <br>
所以我們可以在 JWT token 中加入 `User.id` <br>

<br>

`api/auth.py`
```python
@router.post("/login",response_model=Token)
async def login(form_data: login_form_schema):

    # ...

    return await create_token_pair(
        {"username": user_in_db.name, "id": user_in_db.id},
        {"username": user_in_db.name, "id": user_in_db.id},
    )

@router.post("/refresh",response_model=Token)
async def refresh(refersh_data: RefreshRequest):
    # ...
    u_id:int = payload.get("id")
    if username is None or u_id is None:
        raise  exception_invalid_token

    return await create_token_pair(
        {"username": username , "id": u_id},
        {"username": username , "id": u_id}
    )

```

<br>

回到 `update_user` 中 <br>
我們可以透過 `payload` 來取得 `username` 和 `id` <br>
並且檢查 `id` 是否與 `user_id` 相同 <br>
如果不相同，就回傳 `403 Permission Denied` <br>

<br>

`api/user.py`
```python
@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
# ...
    payload = await verify_access_token(token)
    
    if payload.get("id") != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # ...

```

<br>

當我們以 `test` 用戶的 Token 去打 `PUT /api/users/1` ( `user1` 用戶) 時 <br>
就會回傳 `403 Permission Denied` <br>

![permission denied](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/permission-denied.png)

<br>

改為打自己 ( `test` 用戶) 的 `PUT /api/users/2` 時 <br>
就可以成功更新 <br>

![update user](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day19/update-user.png)

<br>

## Get Current User Dependency

對於需要 Authorize 的 API Endpoint <br>
我們可以透過 `get_current_user` 來簡化取得當前 User 的過程 <br>
讓我們不用再所有的 Route 都寫上 `token:str = Depends(OAuth2PasswordBearer(tokenUrl="api/auth/login"))` 和 `payload = await verify_access_token(token)` <br>

<br>

`auth/utils.py`
```python
from fastapi import HTTPException

from crud.users import UserCrudManager
from schemas.auth import oauth2_token_scheme
from auth.jwt import verify_access_token

UserCrud = UserCrudManager()

async def get_current_user(token = oauth2_token_scheme ):
    payload = await verify_access_token(token)
    
    user_id = int(payload.get("id"))
    user = await UserCrud.get_user_by_id(user_id)

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return user
```

<br>

接下來需要 Authorize 的 API Endpoint <br>
都可以直接使注入`get_current_user` Dependency <br>
來取得當前登入的 User <br>

<br>

`api/user.py`
```python
@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
async def update_user(
    newUser: UserSchema.UserUpdate,
    user_id:int=Depends(check_user_id),
    user = Depends(get_current_user) 
):
    if user.id != user_id:
        raise HTTPException(status_code=403, detail="Permission denied")

    # ...

```

就只需要 `user = Depends(get_current_user)` <br>
就可以取得當前登入的 User <br>
再判斷 `user.id` 是否與 `user_id` 相同即可 <br>

## 總結

今天我們完成了 OAuth2 password login 的實作 <br>
並且實作了 Authorize Dependency 和 權限管理 <br>
也完成 JWT token 的 Refresh 換發機制 <br>

<br>

明天我們把到目前的專案整理一下 <br>
為目前 OAuth2 password login 的實作做一個總結 <br>

## Reference

[FastAPI : OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)