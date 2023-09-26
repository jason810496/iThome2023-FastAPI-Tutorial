# [Day12] 使用 SQLalchemy

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day12 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day12)** <br>

## 回顧

- [Day10](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10) 透過 `create_engine`連接 DB，並能直接透過 argumnets 來切換 DB
- [Day11](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day11) 中，將 `User` 與 `Item` 的 Model 定義好了 <br>

今天我們要將 `User` 與 `Item` 的 CRUD 透過 SQLalchemy ORM 來實現 <br>

## Create 


在 SQLalchemy 中，我們可以透過 `session.add()` 來新增資料，並透過 `session.commit()` 來提交資料 <br>
> 因為我們在 [Day10](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10) 設定 `autocommit=False`，所以我們必須要透過 `session.commit()` 來提交資料 <br>

<br>

`api/user.py` 中的 `create_user`
```python
from models.user import User as UserModel 

# ...
@router.post("/users" ,
        response_model=UserSchema.UserCreateResponse,
        status_code=status.HTTP_201_CREATED,
        response_description="Create new user"
)
def create_user(newUser: UserSchema.UserCreate ):
    # create user
    user = UserModel(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        email=newUser.email,
        avatar=newUser.avatar
    )

    db_session.add(user)
    await db_session.commit()
    return user
```
而 `user` 是我們昨天在 `models/user.py` 中定義的 `User` Model 所建構出來的物件<br>
但會遇到我們回傳的 `user` 是繼承 SQLAlchemy `DeclarativeBase` 的 `UserModel` class <br>
而不是繼承 pydantic 的 `BaseModel` <br>
也不是 `dict` type 所導致的 `response_model` 錯誤 <br>

<br>

![create error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/create-error.png)

<br>

所以可以透過 `db_session.flush()` 來將新的 `user` 寫入 <br>
或是加上 `db_session.refresh(user)` 來更新 `user` <br>
最後再透過 `vars()` 將 `user` 轉換成 `dict` <br>
> 可以參見 [SQLAlchemy : flushing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html#flushing)

`api/user.py`: 使用 `flush()`
```python
    # ...
    db_session.add(user)
    db_session.flush()

    return vars(user)   
```

`api/user.py`: 使用 `refresh()`
```python
    # ...
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return vars(user)   
```


## Read

**在 Create User**

但是剛剛的 `create_user` 應該需要檢查 **email 是否重複** <br>
所以需要先 query 之前是否有相同 `email` 的 user <br>

<br>

在 SQLalchemy 中，目前有兩種 query 的方式：
- 透過`session.query()`
- 先寫出 **statement** 再透過 `session.execute()` 執行或 <br>
    `session.scalars()`取得結果
> 可以參考 [Query guide : The query object](https://docs.sqlalchemy.org/en/20/orm/queryguide/query.html#the-query-object) <br>
> [Quick start : simple select](https://docs.sqlalchemy.org/en/20/orm/quickstart.html#simple-select)

<br>

透過 `session.query()` 來查詢資料 <br>
`api/user.py` 
```python
def create_users(newUser: UserSchema.UserCreate ):
    # check if user already exists
    user = db_session.query(UserModel).filter(UserModel.email == newUser.email).first()
    if user:
        raise HTTPException(status_code=409, detail="User already exists")

    # create user ...
```

<br>

先寫出 **statement** 再透過 `session.execute()` 執行 <br>
`api/user.py` 
```python
def create_users(newUser: UserSchema.UserCreate ):
    # check if user already exists
    stmt = select(UserModel).where(UserModel.email == newUser.email)
    user = db_session.execute(stmt).first() # 使用 execute 就需要使用 first() 來取得結果
    if user:
        raise HTTPException(status_code=409, detail="User already exists")
    
    # create user ...
```

<br>

先寫出 **statement** 再直接透過 `session.scalars()` 取得結果 <br>

`api/user.py` 
```python
def create_users(newUser: UserSchema.UserCreate ):
    # check if user already exists
    stmt = select(UserModel).where(UserModel.email == newUser.email)
    user = db_session.execute(stmt).first()
    if user:
        raise HTTPException(status_code=409, detail="User already exists")

    # create user ...
```

**需要注意：**
直接 `select(UserModel)` 相當於 `SELECT * FROM User` <br>
如果我們只想要取得特定欄位，應該要透過 `select(UserModel.name, UserModel.email, UserModel.xxx )` 來取得 <br>
所以比較正確的寫法應該是 **依據 response schema** 需要的欄位再 `select` <br>

<br>

所以在 create user 前檢查是否已經存在 <br>
只需要 `select(UserModel.id)` 就可以了 <br>
`api/user.py` 
```python
    # stmt = select(UserModel).where(UserModel.email == newUser.email)
    stmt = select(UserModel.id).where(UserModel.email == newUser.email)
    user = db_session.execute(stmt).first()
        if user:
            raise HTTPException(status_code=409, detail="User already exists")
```
> 這邊因為後面的寫法
> 都統一用 `execute` 來寫

**在 Get User By Id**

所以在 `get_user_by_id` 中，就可以依據 `UserRead` 的 Schema 來選取要 `select` 的 column <br>

`api/user.py`
```python
@router.get("/users/{user_id}" , response_model=UserSchema.UserRead )
def get_user_by_id(user_id: int, qry: str = None):
    db_session:Session = get_db()

    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()
    if user:
        return user
        
    raise HTTPException(status_code=404, detail="User not found")
```

### Read List

除了剛剛透過 `select` `where` 來撈出符合特定欄位的單個 user <br>
但 `get_users` 需要回傳所有的 users <br>
所以就不用再加上 `where` 了 <br>

<br>

`api/user.py` 
```python
router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(qry: str = None):
    db_session:Session = get_db()

    stmt = select(UserModel.name,UserModel.id,UserModel.email,UserModel.avatar)

    #...
```
要取得 **整個 List 的 user** 要透過 `execute(stmt).all()` 來取得結果
```python
    # ...
    users = db_session.execute(stmt).all()
    return users
```

## Update

先加上 Update User 的 Schemas <br>
```python
class UserUpdate(UserBase):
    password: Optional[str] = Field(min_length=6)
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0,lt=100)
    birthday: Optional[date] = Field()


class UserUpdateResponse(UserBase):
    avatar: Optional[str] = None
    age: Optional[int] = Field(gt=0,lt=100)
    birthday: Optional[date] = Field()
```

<br>

接著我們可以透過 `update()` 來更新資料 <br>
一開始我們一樣透過 `select()` 來檢查是否有該 User <br>

`api/user.py`
```python
@router.put("/users/{user_id}" , response_model=UserSchema.UserUpdateResponse )
def update_users(user_id: int, newUser: UserSchema.UserUpdate ):
    
    db_session:Session = get_db()

    stmt = select(UserModel.id).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # ...
```

<br>
再完成 update 的 statement <br>

`api/user.py`
```python
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        name=newUser.name,
        password=newUser.password,
        age=newUser.age,
        birthday=newUser.birthday,
        avatar=newUser.avatar
    )

    db_session.execute(stmt)

    return newUser
```

如果只有要 update password ，則只需要在 `values` 的地方加上 `password=newUser.password` 就好

`api/user.py`
```python
@router.put("/users/{user_id}/password", status_code=200)
def update_user_password(user_id : int, newUser:UserSchema.UserUpdatePassword):
    # ...
    stmt = update(UserModel).where(UserModel.id == user_id).values(
        password=newUser.password,
    )
    db_session.execute(stmt)
    db_session.commit()

    return newUser
```

需要注意的是，在執行 `execute` 後 <br>
當前的 DB 連線會自動建立一個 transaction  <br>
直到我們執行 `commit` 後才會完成該 transaction
來避免資料不一致的問題！
> 可以參見 [SQLAlchemy : Commit as you go](https://docs.sqlalchemy.org/en/20/core/connections.html#commit-as-you-go)

## Delete

以 Delete 來說，與前幾個語法都大致相同 <br>
但也需要注意 Delete 的操作要記搭配 `db_session.commit()` <br>
來確實完成整個 transaction <br>

<br>

`api/user.py` 加上 `delete_user`
```python
@router.delete("/users/{user_id}",status_code=status.HTTP_204_NO_CONTENT )
def delete_users(user_id: int):
    db_session:Session = get_db()

    stmt = select(UserModel.id).where(UserModel.id == user_id)
    user = db_session.execute(stmt).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    stmt = delete(UserModel).where(UserModel.id == user_id)
    db_session.execute(stmt)
    db_session.commit()

    return
```


## 測試

### Create 

測試 create user <br>
![create](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/create.png)

在 create 後，嘗試打 get user by id <br>
![create get](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/create-get.png)

### Update

測試 update user by id <br>
![update](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/update.png)

在 update 後，嘗試打 get users <br>
![update get](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/update-get.png)

### Delete

測試 delete user by id <br>
![delete](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/delete.png)

在 delete 後，嘗試打 get user by id <br>
![delete get](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day12/delete-get.png)

## 總結

- `session.add()` 來新增資料，並透過 `session.commit()` 來提交資料 <br>
    並透過 `session.flush()` 或 `session.refresh()` 來更新資料 <br>
- `session.execute()` 執行 **statement** 來查詢資料 <br>
    並使用 `where` 來過濾資料，最後需加上 `first()` 或 `all()` 來取得結果 <br>
- 在使用 `select()` 時，可以透過 `select(UserModel.name,UserModel.email,UserModel.xxx )` 來取得特定欄位 <br>
    不要直接使用 `select(UserModel` 來取得所有欄位 <br>
- 在使用 `update()` 時，可以透過 `update(UserModel).where(UserModel.id == user_id).values(UserModel.name=newName,UserModel.email=newEmail , xxx )` 來更新資料 <br>
    對於想要更新的欄位，可以透過 `values` 來指定 <br>
- 對於 CREATE、UPDATE、DELETE 都需要搭配 `session.commit()` 來確實完成整個 transaction <br>
