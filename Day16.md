# [Day16] 架構優化：非同步存取 DB （2）

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day16 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day16)** <br>

## 回顧

在[昨天(Day15)](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day15)我們完成初步非同步存取 DB 的操作<br>
也透過 `Depends` 將 `AsyncSession` 注入到 CRUD function 中 <br>
我們今天會注重於要如何再次優化我們 CRUD 的架構 <br>
並如何把 `AsyncSession` 的 Dependency Injection 做的更好 <br>

## CRUD Class

目前的寫法都是將 CRUD 分寫成 function 如： `get_users` 、 `get_user_id_by_email` 、 `create_user` 等<br>
但是我們也可以將所有得 CRUD functions 都包裝在 class 中 <br>

`crud/users.py`
```python
class UserCrud:
    def __init__(self,db_session:AsyncSession):
        self.db_session = db_session
    async def get_users(self,db_session:AsyncSession, keyword:str=None,last:int=0,limit:int=50):
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)
        result = await db_session.execute(stmt)
        users = result.all()

        return users
    # ... CRUD functions

async def get_user_crud():
    async with get_db() as db_session:
        yield UserCrud(db_session)
```

這樣的好處是：我們不需要為每個 CRUD function 都注入 `AsyncSession` <br>
可以直接透過 `Depends(get_user_crud)` 來取得 `UserCrud` class 來操作 <br>

<br>

`api/users.py`
```python
from crud.users import UserCrud , get_user_crud_manager

# ... 

db_depends = Depends(get_user_crud) # <--- 修改

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
async def get_users(page_parms:dict= Depends(pagination_parms), userCrud:UserCrud=db_depends):
    users = await userCrud.get_users(**page_parms)
    return users
```


## Depends 與 yield 常見錯誤

在使用 `Depends` 與 `yield` 時，常見的錯誤如下：
我們可能會想：「如果要在 `api/users.py` 中使用 `Depends(get_user_crud)` 來取得 `UserCrud` class 來操作」<br>
為什麼不直接在 `crud/users.py` 中使用 `Depends(get_db)` 來取得 `AsyncSession` 來操作呢？ <br>
`crud/users.py`
```python

class UserCrud:
    def __init__(self):
        self.db_session = Depends(get_db) # <--- 修改
    async def get_users(self,db_session:AsyncSession, keyword:str=None,last:int=0,limit:int=50):
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        if keyword:
            stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
        stmt = stmt.offset(last).limit(limit)
        result = await db_session.execute(stmt)
        users = result.all()

        return users
    # ... CRUD functions
```
直接這樣寫的話，會報錯如下：
![depends crud error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day16/depends-crud-error.png)
寫著 `AttributeError: 'Depends' object has no attribute 'execute'` ：`Depends` 沒有 `execute` 的屬性 <br>
但依照我們的邏輯，`self.db_session` 應該是 `AsyncSession` 才對啊（？ <br>
這是因為在 FastAPI 中，**`Depends` 必須要寫在 API endpoint 的 handle funtion 中** ! <br>
也就是說，我們只能在 `api/users.py` 中使用 `Depends(get_user_crud)` 來取得 `UserCrud` class 來操作 <br>
或是透過 `Depends(get_db)` 來注入 `AsyncSession` 到 CRUD function 中 <br>

<br>
<br>

那可能又會想說：「為什麼一定要透過 `Depends` 來取得 `AsyncSession` 呢？ <br>
應該也可以直接在 `crud/users.py` 中使用 `async with get_db() as db_session` 來取得 `AsyncSession` 才對啊（？ <br>

<br>

`crud/users.py`
```python
# ...

  async def get_users(self,keyword:str=None,last:int=0,limit:int=50):
        async with get_db() as db_session: # <--- 新增 
            stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
            if keyword:
                stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
            stmt = stmt.offset(last).limit(limit)
            # result = await self.db_session.execute(stmt)
            result = await db_session.execute(stmt)
            users = result.all()

            return users
```

<br>

這樣寫的話，會報錯如下：
![without depends error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day16/without-depends-error.png)

寫著 `TypeError: 'async_generator' object does not support the asynchronous context manager protocol` <br>
查看 [FastAPI Doc 中，與 Depends 和 yield 相關的部分](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/) <br>
上面提到 [@contextlib.asynccontextmanager](https://docs.python.org/3/library/contextlib.html#contextlib.asynccontextmanager) <br>
稍微了解後，我們可以知道 `async with` 是 `async` 的 context manager <br>
`async_generator` 不支援 `async` 的 context manager <br>


## AsyncSession `asynccontextmanager` dependency

上面提到的問題 <br>
> `async with` 是 `async` 的 context manager <br>
> `async_generator` 不支援 `async` 的 context manager <br>

<br>

我們可以透過 `@contextlib.asynccontextmanager` 來將 `async_generator` 轉換成 `async` 的 context manager <br>
所以應該要為 `get_db` 加上 `@contextlib.asynccontextmanager` <br>

<br>

`database/generic.py`
```python

from contextlib import asynccontextmanager

@asynccontextmanager # <--- 新增
async def get_db():
    async with SessionLocal() as db:
        async with db.begin():
            yield db
# ...
```

<br>

那上面直接使用 `async with get_db() as db_session` 來取得 `AsyncSession` 操作 DB 的方式就可以了 ! <br>

`crud/users.py`
```python

# ...

async def get_users(self,keyword:str=None,last:int=0,limit:int=50):
        async with get_db() as db_session:
            stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
            if keyword:
                stmt = stmt.where(UserModel.name.like(f"%{keyword}%"))
            stmt = stmt.offset(last).limit(limit)
            # result = await self.db_session.execute(stmt)
            result = await db_session.execute(stmt)
            users = result.all()

            return users

# ...
```
現在這樣寫就可以正常執行了！ <br>

## 使用 `decorator` 來注入 `AsyncSession`

雖然我們現在可以透過 `async with get_db() as db_session` 直接來取得 `AsyncSession` 操作 DB <br>
可以不用透過 FastAPI 中的 `Depends` 來達成 <br>
> 但是我們還是需要在每個 CRUD function 中都寫上 `async with get_db() as db_session` <br>
> 並多一個縮排 <br>

<br>

- `decorator` for function 
所以我們可以透過 `decorator` 來將 `async with get_db() as db_session` 注入到 CRUD function 中 <br>

`database/generic.py`
```python

# ...

# decorator dependency for getting db session

def db_session_decorator(func):
    # print("in db_context_decorator")
    async def wrapper(*args, **kwargs):
        async with get_db() as db_session:
            kwargs["db_session"] = db_session
            result = await func(*args, **kwargs)
            return result
    # print("out db_context_decorator")
    return wrapper
```
在 `wrapper` function 中，我們為接下來要掛上 `@db_session_decorator` decorator 的 `func` 中 <br>
 `db_session` 參數設為 `AsyncSession` <br>
所以在原本的 CRUD function 中，我們只需要要加上 `db_session` 參數和 `@db_session_decorator` <br>
就可以注入 `AsyncSession` 使用了 <br>

<br>

`crud/users.py`
```python
# ...
from database.generic import db_session_decorator # <--- 新增

# ...

class UserCrudManager: # <--- 修改

    @db_session_decorator # <--- 新增
    async def get_users(self,db_session:AsyncSession, keyword:str=None,last:int=0,limit:int=50):
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        # ...
        return users

    @db_session_decorator # <--- 新增
    async def get_user_by_id(self,user_id: int):
        # ...
    # ... CRUD functions
```

<br>

- `decorator` for class

但是這樣的寫法，我們還是需要在每個 CRUD function 中都寫上 `db_session` 參數和 `@db_session_decorator` <br>
所以我們可以透過為 `UserCrudManager` 加上 `decorator` <br>
來為所有 methods 都加上 `@db_session_decorator` <br>
這邊我們透過 `setattr` 來為 `cls` 中的每個 methods 都加上 `db_session_decorator` <br>

<br>

`database/generic.py`
```python
# ...

def crud_class_decorator(cls):
    # print("in db_class_decorator")
    for name, method in cls.__dict__.items():
        if callable(method):
            setattr(cls, name, db_session_decorator(method))
    # print("out db_class_decorator")
    return cls
```
我們只需要為 `UserCrudManager` 加上 `@crud_class_decorator` <br>
並為每個 CRUD methods 加上 `db_session` 參數 <br>

<br>

`crud/users.py`
```python

# ...

@crud_class_decorator # <--- 新增
class UserCrudManager:

    # 為每個 CRUD methods 加上 db_session 參數
    async def get_users(self,db_session:AsyncSession, keyword:str=None,last:int=0,limit:int=50): # <--- 修改
        stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)
        # ...
        return users

    async def get_user_by_id(self,db_session:AsyncSession,user_id: int): # <--- 修改
        # ...
    # ... CRUD functions
```

<br>

## 使用 `UserCrudManager` instance 來操作 CRUD

修改完後，只需要在 `api/users.py` 建立一個 `UserCrudManager` 的 instance <br>
就可以透過 `instanceName.action` 來操作 CRUD 了 <br>

`api/users.py`
```python
# ...

# from crud import users as UserCrud # <--- 刪除
from crud.users import UserCrudManager

UserCrud = UserCrudManager()
# 這邊我們同樣民名為 UserCrud ，但是實際上是 UserCrudManager 的 instance

# ...

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
async def get_users(page_parms:dict= Depends(pagination_parms), userCrud:UserCrud=db_depends):
    users = await UserCrud.get_users(**page_parms)
    return users

# ... API endpoints
```

<br>

再跑一次昨天的 benchmark 來比較一下
> `ab -n 50000 -c 32 http://127.0.0.1:8001/sync/api/users` 
- 昨天的
![bench 50000 32 async](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day15/bench-50000-32-async.png)
- 今天的
![bench 50000 32 async](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day16/bench-50000-32-async.png)

<br>

昨天以 `Depends` 注入 `AsyncSession` 總時間約 105 秒 <br>
今天透過 `asynccontextmanager` 與 `decorator` 注入 `AsyncSession` 總時間約 98 秒 <br>
可以看到效能上有稍微提升 <br>
從 sync CRUD 修改成 async CRUD 要更新的 code 也比較少 <br>

## 總結

- 常見 `Depends` 與 `yield` 的錯誤 <br>
- 透過 `@contextlib.asynccontextmanager` 來將 `async_generator` 轉換成 `async` 的 context manager <br>
- 透過 `decorator` 來注入 `AsyncSession` <br>
    - `decorator` for function 
    - `decorator` for class
- 使用 `UserCrudManager` instance 來操作 CRUD <br>

<br>
