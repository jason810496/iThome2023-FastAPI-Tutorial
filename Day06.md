# [Day06] Response model

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day06 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day06)** <br>

## 昨天回顧

昨天我們介紹了 `Pydantic` 的基本使用 <br>
可以透過 Schema 來定義我們 request body 的格式 <br>

今天我們要來介紹如何透過 Schema 搭配 `Response model` 來定義我們 **response body** 的格式 <br>

## Response model

在 FastAPI 中，我們可以在 decorator 中加上 `response_model` <br>
從 `main.py` 中的 `create_users` 這個 api endpoint 下去改 <br>
```python
@app.post("/users" , response_model=UserSchema ) # response_model 是新加上的
def create_users(user: UserSchema):
    fake_db["users"][user.id] = user
    return user
```

可以看到更新到 Swagger UI 後，我們的 Response 會多出一個 `Response body` 的格式 <br>
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day06/responce-swagger.png)

## Schema 與 Response model / Request body

一般來說，我們會依據 CRUD 定義對應的 Request / Response Schema <br>
如 `UserCreate` , `UserUpdate` , `UserRead` , `UserDelete` 等<br>

`schemas/user.py`
```python
class UserBase(BaseModel):
    name: str

class UserCreate(UserBase):
    age: int
    email: str
    birthday: date

class UserRead(UserBase):
    email: str
```
可以看到 `UserCreate` , `UserRead` , `UserDelete` 都繼承了 `UserBase` <br>
> 可以把共用的欄位放在 `UserBase` 中 ！


接著我們更新 `main.py` 中 import 的 user schema 結構 <br>
```python
# from schemas.users import User as UserSchema # 舊的
from schemas import users as UserSchema # 新的
```

更新 user API endpoint 的 request / response model <br>
這次我們順便加上 `delete_users` 的 api endpoint <br>
```python
@app.post("/users" , response_model=UserSchema.UserCreate )
def create_users(user: UserSchema.UserCreate ):
    fake_db["users"][user.id] = user
    return user

@app.delete("/users/{user_id}" )
def delete_users(user_id: int):
    user = fake_db["users"].pop(user_id)
    return user

@app.get("/items/{item_id}" , response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id : int , qry : str = None ):
    if item_id not in fake_db["items"]:
        return {"error": "Item not found"}
    return fake_db['items'][item_id]
```

## Response model 的其他功能

一樣先到 Swagger UI 測試看看 <br>
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day06/swagger.png)

在 get user 的 api endpoint 中，我們可以看到 `Response body` 的格式 <br>
只剩下 `name` 和 `email` 兩個欄位 <br>
在打 API 的結果也確實只得到這兩個欄位的結果 <br>
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day06/get-user.png)

但是我們回來看一下 `fake_db` , `get_users` 和 `UserSchema.UserRead` 個別的定義 <br>

`fake_db`
```python
fake_db = {
    "users": {
        1: {
            "name": "John",
            "age": 35,
            "email": "john@fakemail.com",
            "birthday": "2000-01-01",
        },
        # ...
    }
}
```
`get_users`
```python
@app.post("/users" , response_model=UserSchema.UserCreate )
def create_users(user: UserSchema.UserCreate ):
    fake_db["users"][user.id] = user
    return user
```
`UserSchema.UserRead`
```python
class UserRead(UserBase):
    email: str
```

在 `get_users` 中，我們回傳的是 `fake_db['users'][user_id]` <br>
那根據 `fake_db` 應該回傳的欄位包括：
- `name`
- `age`
- `email`
- `birthday`

但是因為我們在 `get_users` 中加上了 `response_model=UserSchema.UserRead` <br>
而 `UserSchema.UserRead` 中只有 `name` 和 `email` 兩個欄位 <br>
所以在回傳結果中，只剩下:
- `name`
- `email`

經過這個測試，我們可以發現 `response_model` 除了可以定義 response body 的格式 <br>
也可以**過濾掉 schema 中沒有提到的欄位** <br>
即使原本 return 的資料中有這些欄位，但是在 response 不會拿到 <br>

## 更新 items 相關
### 更新 item Schema 

接著我們來更新 `item` 的 Schema <br>

`schemas/items.py`
```python
class ItemBase(BaseModel):
    id: int

class ItemCreate(ItemBase):
    name: str
    price: float
    brand: str

class ItemRead(ItemBase):
    name: str
    price: float
```

更新 `main.py` 中 import 的 item schema 結構 <br>
```python
# from schemas.items import Item as ItemSchema # 舊的
from schemas import items as ItemSchema # 新的
```

### 更新 item API endpoint

更新 `main.py` 中的 item API endpoint <br>
```python
@app.get("/items/{item_id}" , response_model=ItemSchema.ItemRead)
def get_item_by_id(item_id : int , qry : str = None ):
    if item_id not in fake_db["items"]:
        return {"error": "Item not found"}
    return fake_db['items'][item_id]

@app.post("/items" , response_model=ItemSchema.ItemCreate)
def create_items(item: ItemSchema.ItemCreate ):
    fake_db["items"][item.id] = item
    return item

@app.delete("/items/{item_id}")
def delete_items(item_id: int):
    item = fake_db["items"].pop(item_id)
    return item
```

## Response model 總結

- 在 FastAPI 中，我們可以在 decorator 中加上 `response_model=OurSchema` <br>
- 可以透過 `response_model` 來定義我們 **response body** 的格式 <br>
- 也可以**過濾掉 schema 中沒有提到的欄位** ( 即使有 return 更多資訊 ) <br>

目前進度:
`/backend` 目錄結構
```
.
├── main.py
├── run.py
├── schemas
│   ├── items.py
│   └── users.py
└── setting
    ├── .env.dev
    ├── .env.prod
    ├── .env.test
    └── config.py

2 directories, 8 files
```
Swagger UI
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day06/swagger-cur.png)

#### 參考資料

- [FastAPI - Response model](https://fastapi.tiangolo.com/tutorial/response-model/)

