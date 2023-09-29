# [Day14] 架構優化：將 CRUD 與 API endpoint 分離

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day14 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day14)** <br>

## 回顧

我們從 [Day10](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10) 開始設定 DB 和 SQLAlchemy <br>
並完成 User 基本操作的 CRUD <br>
但是我們跟 DB 有關 CRUD 的操作都寫在 `api/users.py` 裡面 <br>

## 將 CRUD 與 API endpoint 分離

在 FastAPI 架構中<br>
我們通常會將 CRUD 與 API endpoint 分離 <br>

<br>

建立 `crud/users.py` 和 `crud/items.py` <br>

```bash
mkdir crud
touch crud/{users,items}.py
```

<br>

在 `crud/users.py` 中引入會用到的 modules <br>
並建立 `db_session` <br>

```python
from sqlalchemy.orm import Session 
from sqlalchemy import select , update , delete
import hashlib


from database.generic import get_db
from models.user import User as UserModel 
from schemas import users as UserSchema

db_session:Session = get_db()

# ... TBA 
```

### Create User

並將 `api/users.py` 中的 CRUD 操作移動到 `crud/users.py` <br>
如原本 create user 的 API endpoint 中<br>
可以分為：
- `get_user_id_by_email`
- `create_user`
這兩個 DB 相關的操作 <br>
所以在 `crud/users.py` 中建立這兩個 function <br>

<br>

`crud/users.py` 中加入 `get_user_id_by_email`<br>
```python

def get_user_id_by_email(email: str):
    stmt = select(UserModel.id).where(UserModel.email == email)
    user = db_session.execute(stmt).first()
    if user:
        return user
        
    return None
```

<br>

`crud/users.py` 中加入 `create_user`<br>
```python
def create_user(newUser: UserSchema.UserCreate ):
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

    return user
```

<br>

經過上面的步驟後<br>
原本在 `api/users.py` 中的 create user API endpoint 包含 <br>
許多操作 DB 的動作都被切割至 `crud/users.py` 中 <br>

`api/users.py` old version : 
```python
    stmt = select(UserModel.id).where(UserModel.email == email)
    db_session...
    # ...
    if user:
        raise # ...
    # ...

    user = UserModel(
        name=newUser.name,
        # ...
    )
    db_session.add(user)
    db_session...
    # ...
```

<br>

`api/users.py` new version : 
```python
from crud import users as UserCrud

# ...

@router.post("/users" ,
        response_model=UserSchema.UserCreateResponse,
        status_code=status.HTTP_201_CREATED,
        response_description="Create new user"
)
def create_user(newUser: UserSchema.UserCreate ):
    user = UserCrud.get_user_id_by_email(newUser.email)
    if user:
        raise HTTPException(status_code=409, detail=f"User already exists")
    
    user = UserCrud.create_user(newUser)
    return vars(user)
```

可以看到更新過的 API Endpoint 看起來就整潔許多 <br>
如果需要修改 DB 的操作，再回到 `crud/users.py` 中修改相對應的 function 即可 <br>

### Get Users

如果有帶入 `keyword` 的話，我們會透過 `keyword` 來搜尋 `name` <br>
而 `last` 和 `limit` 則是用來做分頁 <br>
`crud/users.py` 中加入 `get_users`<br>
```python
def get_users(keyword:str=None,last:int=0,limit:int=50):
    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
    if keyword:
        stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
    stmt = stmt.offset(last).limit(limit)
    users =  db_session.execute(stmt).all()

    return users
```

<br>


我們在 [Day13](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day13) 為 get_users 加上了 `pagination_parms` 的 `Depends` <br>
而 `pagination_parms` 回傳的是 `{keyword:str, limit: int, offset: int}`的 `dict` <br>
這邊我們可以使用一個 python 的語法糖，可以將 `Depends` 回傳的 `dict` 轉換成 `**kwargs` <br>

<br>

`api/users.py` 中修改 get_users<br>
```python
@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(page_parms:dict= Depends(pagination_parms)):
    # users = UserCrud.get_users(
    #     page_parms["keyword"],
    #     page_parms["last"],
    #     page_parms["limit"]
    # )
    users = UserCrud.get_users(**page_parms)
    return users
```

## 總結

將 CRUD 與 API endpoint 分離後<br>
我們 API endpoint 的程式碼看起來就整潔許多 <br>
可以直接以 `TypeCrud.action_name` 的方式呼叫 CRUD 的操作或是取得資料 <br>
將專案的架構分離後，也可以讓我們更容易維護 <br>

<br>
