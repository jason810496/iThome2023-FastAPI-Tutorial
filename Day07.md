# [Day07] 再談 Python Typing 與 Schema 常見錯誤

## 回顧

- [[Day04]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day04) FastAPI 基礎架構
- [[Day05]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day05) Schema & Pydanic
- [[Day06]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day06) Response model

我們目前已經知道如何使用 FastAPI 來建立一個簡單的 API，並且使用 Pydantic 來定義 Schema，並且使用 Response model 來定義回傳的資料格式。接下來我們將會再談談 Python Typing 與 Schema 常見錯誤。

## Schema 常見錯誤

### 專案結構調整
在看這個錯誤之前，我們先來調整一下目前的專案結構 <br>
先將原本 `main.py` 中的 `fake_db` 移到 `database/fake_db.py` 中

```bash
mkdir database
touch database/fake_db.py
```

並為 `fake_db['users']` 加上 `id` 、 `password` 和 `avatar` 欄位

```python
fake_db = {
    "users": {
        1: {
            "id": 1,
            "password": "John",
            "avatar": "https://i.pravatar.cc/300",
            "name": "John",
            "age": 35,
            "email": "john@fakemail.com",
            "birthday": "2000-01-01",
        },
        2: {
            "id": 2,
            "password": "Jane",
            "avatar": None,
            "name": "Jane",
            "age": 25,
            "email": "jane@fakemail.com",
            "birthday": "2010-12-04",
        }
    },
    "items":{
        #...
    }
}
```
在 `main.py` 中引入 `database.fake_db` 並調整 `get_db` 的回傳值
```python

from database.fake_db import get_db

# ...

fake_db = get_db()

# ...

```

再次調整 user 的 schema
`schemas/user.py`
```python
class UserBase(BaseModel):
    id: int

class UserCreate(UserBase):
    password: str # 新增 password 欄位
    name: str
    avatar: str # 新增 avatar 欄位
    age: int
    email: str
    birthday: date

class UserRead(UserBase):
    name: str
    email: str
    avatar: str
```

### Schema 常見錯誤 1

在調整完專案結構後 ( 剛剛為 `UserCreate` 加上 `password` 和 `avatar` 欄位 ) <br>
我們來看看第一個 schema 常見錯誤 <br>
我們先來測試 create user 的 API

![create user plaintext](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day07/create-user-plaintext.png)

會發現 Response model 如果同樣也使用 `UserCreate` 的話 <br>
其中的 `password` 會以**明文的方式**回傳 <br>
這是非常危險的 !!!

<br>

所以正確來說，我們應該還再需要寫一個 `UserCreateResponse` <br>
作為 create user 的 `response_model` <br>

`schemas/user.py`
```python

class UserCreateResponse(UserBase):
    name: str
    email: str
```

`main.py` 的 `create_user` API
```python
@app.post("/users" , response_model=UserSchema.UserCreateResponse ) # 改為 UserCreateResponse
def create_users(user: UserSchema.UserCreate ):
    fake_db = get_db()
    fake_db["users"][user.id] = user
    return user
```

更新過後的 API Response :
![create user fix](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day07/create-user-fix.png)

<br>

第一個常見的錯誤就是，沒有為 **涵蓋敏感資訊** 的 API <br>
設定專屬的 response schema ! <br>

### Schema 常見錯誤 2

接下來我們來看看第二個 schema 常見錯誤 <br>
先來打一下 GET `/users/2` 的 API 看看

![get user 2](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day07/get-user-2.png)

發現回傳 `500 Internal Server Error` <br>
看一下 server 的 log 

![500 log](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day07/500-log.png)
上面寫著 `avatar` should be valid string <br>
但 input 的是 `None` <br>

<br>

我們檢查一下 `fake_db` 中 `users[2]` 的資料
```python
2: {
        "id": 2,
        "password": "Jane",
        "avatar": None,
        "name": "Jane",
        "age": 25,
        "email": "jane@fakemail.com",
        "birthday": "2010-12-04",
    }
```
因為 `avatar` 欄位是 `None` <br>
導致 `pydantic` 驗證失敗 <br>
所以對於 **可能為 null(None)** 的欄位 <br>
我們應該要使用 `Optional` 或 `Union` 來定義 <br>

## 再談 Python Typing 

### Optional & Union

我們可以從 `typing` 中引入 `Optional` 和 `Union` <br>
`Optional` 用來定義 **可能為 null(None)** 的欄位 <br>

`schemas/user.py`
```python
from typing import Optional

class UserRead(UserBase):
    class UserRead(UserBase):
    name: str
    email: str
    avatar: Optional[str] = None
```
並且使用 `Optional` 的話，必須要有賦予值 <br> 
這邊讓 `avatar` 的預設值為 `None` <br>

<br>

除了 `Optional` 我們也可以透過 `Union` 的方式來定義可能為 null 的欄位 <br>
`schemas/user.py`
```python
from typing import Union

class UserRead(UserBase):
    class UserRead(UserBase):
    name: str
    email: str
    avatar: Union[str,None] = None
```

接著去打一個 user 沒有 `avatar` 的 API  <br>

![get user 2 fix](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day07/get-user-2-fix.png)

## 更新其他 API

我們假設 user 的 `avatar` 可以不填寫 ( 可能有用戶不想要設定頭像 ) <br>
所以在 create user 的 API 中，我們也要將 `avatar` 設定為 `Optional` <br>

`schemas/user.py`
```python
class UserCreate(UserBase):
    password:str
    name: str
    avatar: Optional[str] = None
    age: int
    email: str
    birthday: date
```

再以不帶入 `avatar` 的情況打 create user 的 API <br>
![create user fix](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day07/create-user-fix.png)
也不會報錯了 <br>


## 總結

- 涵蓋敏感資訊的 API 要記得設定專屬的 response schema
- 對於可能為 null 的欄位，使用 `Optional` 或 `Union` 來定義






