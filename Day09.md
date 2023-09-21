# [Day09] 架構優化：依據項目切分 Router

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day07 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day08)** <br>

## 回顧

在 [Day04](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day04) 到 [Day08](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day08) 中 <br>
我們知道:
- FastAPI 的架構
- 如何使用 Typing 和 Pydantic 定義 Schema
- `response_model` 的用法
- 如何在 Swagger 中加入更多資訊


那今天我們今天來優化目前專案的架構 <br>
因為目前所有 router 都放在 `main.py` 中，會讓程式碼變得難以維護 <br>

## 依據項目切分 Router

一般在 FastAPI 專案中 <br>
我們會將所有 API 的 router 都放在特定資料夾中 <br>
常見的命名有: `routers` 、 `api` 或 `endpoints` <br>

在這邊我們使用 `api` 這個名稱 <br>

首先我們先在專案中新增一個 `apis` 資料夾 <br>
並在 `api` 中新增一個 `__init__.py` <br>
```python
mkdir api
touch api/__init__.py
touch api/{users,items}.py
```

接著我們將 `main.py` 中 users 相關的 router 移動到 `api` 中 
<br>
所以會使用到 FastAPI 中的 `APIRouter` <br>

`api/users.py`
```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/users")
async def read_users():
    return [{"username": "Foo"}, {"username": "Bar"}]
```
而 `APIRouter` 的用法和原本 `main.py` 中的 `app` instance 一樣 <br>
都是透過 decorator 來定義 <br>
所以只要將 `main.py` 中的 `app` 改成 `router` 即可 <br>

更新完整的 `api/users.py` 如下
```python
from fastapi import APIRouter, HTTPException, status
from typing import List , Dict

from schemas import users as UserSchema
from database.fake_db import get_db

fake_db = get_db()

router = APIRouter()

@router.get("/users", 
        response_model=List[UserSchema.UserRead],
        response_description="Get list of user",  
)
def get_users(qry: str = None):
    """
    Create an user list with all the information:

    - **id**
    - **name**
    - **email**
    - **avatar**

    """
    return fake_db['users']

# ....
# 剩下的可以到 Day08 的 repo 中看程式碼
```


## 將 router 加入到 `main.py` 中

接著我們要將 `api/users.py` 中的 router 加入到 `main.py` 中 <br>
所以我們要使用到 FastAPI 中的 `include_router` <br>

`main.py`
```python
from fastapi import FastAPI 

from api.users import router as users_router

app = FastAPI()

app.include_router(users_router)
```
就可以將 `api/users.py` 中的 router 加入到 `main.py` 中 <br>

## 專案架構調整

接著把剩下與 items 相關的 router 也分切加入到 `api/items.py` 中 <br>
而最後 `/` 與 `/infor` 放到 `api/infor.py` 中 <br>
調整完成後的專案架構如下 <br>

```
.
├── api
│   ├── infor.py
│   ├── items.py
│   └── users.py
├── database
│   └── fake_db.py
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

4 directories, 12 files
```

## tags 

到 Swagger 中可以看到 <br>
![swagger orig](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day08/swagger-orig.png)<br>
所有的 API 都與之前相同 <br>
但我們還可以為 API 加上 **`tags`** <br>
`tags` 的用途是可以讓我們在 Swagger 中將 API 分類 <br>

`api/users.py`
```python
# ...
from fastapi import APIRouter

router = APIRouter(
    tags=["users"] # <-- tags
)


@router.get("/users")
# ...
```

`api/items.py` 與 `api/infor.py` 也加上 `tags` 後 <br>
再次到 Swagger 中看看 <br>

![swagger tags](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day09/swagger-tags.png)<br>

在 Swagger 中每個類別的 API 都依照 `tags` 分在不同區塊 <br>
這樣就可以讓我們的 Swagger 更結構化 <br>

## prefix

接著我們可以為每個 router 加上 **`prefix`** <br>
`prefix` 的用途是可以讓我們在 `APIRouter` 中加上前綴 <br>
一般來說在後端 API 會加上 `/api` 作為前綴 <br>

`api/users.py`
```python
# ...
router = APIRouter(
    tags=["users"],
    prefix="/api" # <-- prefix
)

# ...
```

`api/items.py` 也加上 `prefix` 後 <br>
再次到 Swagger 中看看 <br>

![swagger prefix](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day09/swagger-prefix.png)<br>

可以看到 Swagger 中的 users 與 items 的 API 都被加上 `/api` 作為前綴 <br>

## 總結

今天我們學到:
- 依據項目切分 router
- 將個別 router 加入到 `main.py` 中
- 使用 `tags` 來調整 Swagger 的顯示
- 使用 `prefix` 來為 API 加上前綴