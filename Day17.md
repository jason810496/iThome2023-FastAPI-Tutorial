# [Day17] OAuth2 實例： 密碼驗證

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day17 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day17)** <br>


## 回顧

我們在 [Day15](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day15) 和 [Day16](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day16) 完成 async CRUD 的實作 <br> 
今天會開始進入 **OAuth2 password login的實作** <br>
首先我們會先實作 **密碼驗證** <br>

## 密碼驗證

### 關於在 DB 中儲存密碼

如果要在 DB 中儲存密碼，我們**不能直接儲存明碼**! <br>
而是要將密碼進行加密後再儲存 <br>
常見的做法會是：<br>
```
hash_password = hash_function(plain_password + salt)
```
這邊我們使用 [`bcrypt`](https://zh.wikipedia.org/zh-tw/Bcrypt) 密碼雜湊函數來進行加密 <br>

<br>

`passlib` 是一個密碼雜湊函數的套件，我們可以透過 `passlib` 來進行密碼的加密與驗證 <br>
```bash
poetry add passlib
poetry add bcrypt
```

<br>

新增 auth 目錄 <br>
```bash
mkdir auth
touch auth/passwd.py
```

## 調整 User Model

因為 `passlib` 使用 `bcrypt` 生成 hash password 的長度為 60，所以我們要調整 `User` model <br>

`models/base.py`
```python
class BaseType:
    # ...
    str_60 = Annotated[str, mapped_column(String(60))] # 新增 str_60
    # ...

```

<br>

`models/user.py`
```python
# ...
class User(BaseType, Base):
    __tablename__ = "User"
    id:Mapped[BaseType.int_primary_key]
    password:Mapped[BaseType.str_60]
    # ...
```

<br>

> 因為我們要調整 `User` model，所以要先把 `User` table 刪除 <br>
> 可以直接進入 PostgreSQL 的 container 中，透過 `psql` 來刪除 table <br>
> 也可以砍掉 PostgreSQL 的 container 和 **對應的 volumn** 再重新建立 <br>

<br>

## 透過 `passlib` hash 密碼、驗證密碼

接著在 `auth/passwd.py` 中撰寫 hash 與驗證密碼的 function <br>

<br>

`auth/passwd.py`
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)
```


## 調整 `create_user` API endpoint

接著我們要調整 `create_user` API endpoint <br>
把原本以明碼儲存的密碼，改成 hash 過的密碼存在 DB 中 <br>

<br>

`routers/user.py` 中的 `create_user` 
```python
from auth.passwd import get_password_hash

# ...

@router.post("/users" ,
        response_model=UserSchema.UserCreateResponse,
        status_code=status.HTTP_201_CREATED,
        response_description="Create new user"
)
async def create_user(newUser: UserSchema.UserCreate ):
    user = await UserCrud.get_user_id_by_email(newUser.email)
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")
    
    newUser.password = get_password_hash(newUser.password) # <--- 新增這行
    user = await UserCrud.create_user(newUser)
    return vars(user)
```

## 進入 container 中的 postgresql 檢查 user table

可以連進 PostgreSQL 的 container 中，透過 `psql` 來查看 `user` table 中 <br>
user 的 password 欄位是不是被 hash 過的密碼 <br>
```bash
docker exec -it fastapi_postgres_dev psql -U fastapi_tutorial
```
<br>

進入 PostgreSQL 後，可以順便檢查 SQLAlchemy 產生的 table schema 是否正確 <br>
```sql
```sql
\l -- list all databases
\c fastapi_tutorial -- connect to fastapi_tutorial database
\dt -- list all tables
\d "User" -- describe table "User"
```

![docker exec psql]()

<br>

接著我們可以透過 `SELECT` 指令來查看 `User` table 中的資料 <br>
```sql
SELECT * FROM "User";
```

![select users]()

可以看到 `password` 欄位中的密碼都是 hash 過的密碼 ! <br>

## 總結

今天我們透過 `passlib` 來進行密碼的 hash 與驗證 <br>
並且透過 `bcrypt` 來進行 hash <br>
最後我們也透過 `psql` 來檢查 `User` table 中的密碼是否被 hash 過 <br>

<br>

接下來我們會繼續完成 OAuth2 password login 的實作 <br>
明天會接著講 `fastapi.security` 中提供與 OAuth2 相關的 schema ! <br>


#### Reference

[FastAPI : OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)