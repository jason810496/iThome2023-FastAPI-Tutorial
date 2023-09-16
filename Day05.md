# [Day05] Schema & Pydantic

## 昨天談到什麼？

- Typing
- Path parameter
- Query parameter

昨天都在談 `Path parameter` 和 `Query parameter` 的 Typing ，但是我們沒有談到 `body` 的部分 <br>
所以今天就先從 `pydantic` 開始談起吧 ！

## Pydantic

`pydantic` 是一個專門用來驗證資料類別的套件 <br>
如這個 `User` class 的 id 必須為 int ， name 必須為 str ， birthday 必須為 date <br>
並且 `User` 需要繼承 `BaseModel` ！ <br>
而這個專門用來驗證資料類的 class 我們稱之為 **`schema`** <br>
> 測試 code 在 [PydanticExample/test.py]()
```python
from datetime import date

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    birthday: date

    def __str__(self):
        return f'User(id={self.id}, name={self.name}, birthday={self.birthday})'

try :
   User(id=1, name='John', birthday=date(2000, 1, 1))
except Exception as e:
    print(e)

try :
    User(id='str', name='John', birthday=date(2000, 1, 1))
except Exception as e:
    print(e)
```

如果我們在創建 `User` 的 instance 時，傳入的參數不符合 `User` 的 schema <br>
那麼就會報錯 <br>
```
User(id=1, name=John, birthday=2000-01-01 00:00:00)
1 validation error for User
id
  Input should be a valid integer, unable to parse string as an integer [type=int_parsing, input_value='u_id', input_type=str]
    For further information visit https://errors.pydantic.dev/2.3/v/int_parsing
```

## Pydantic 的常用 decorator

`@validator` 可以用來驗證 `schema` 的資料 <br>
```python
from datetime import date

from pydantic import BaseModel, validator

class User(BaseModel):
    id: int
    name: str
    birthday: date

    @validator('id')
    def id_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('id must be positive')
        return v

    @validator('name')
    def name_must_be_capitalized(cls, v):
        if v[0].islower():
            raise ValueError('name must be capitalized')
        return v

    @validator('birthday')
    def birthday_must_be_after_2000(cls, v):
        if v.year < 2000:
            raise ValueError('birthday must be after 2000')
        return v 
```

## FastAPI 中的 Schema

### 加入假資料

在這次的範例中，我們會使用到假資料 <br>
在 `main.py` 中，我們可以加入 `fake_db` <br>
( 在正式專案中不會這樣寫！ ) <br>
```python
# from fastapi import FastAPI
# ...

# fake db
fake_db = {
    "users": {
        1: {
            "name": "John",
            "age": 35,
            "email": "john@fakemail.com",
            "birthday": "2000-01-01",
        },
        2: {
            "name": "Jane",
            "age": 25,
            "email": "jane@fakemail.com",
            "birthday": "2010-12-04",
        }
    },
    "items": {
        1: {
            "name": "iPhone 12",
            "price": 1000,
            "brand": "Apple"
        },
        2: {
            "name": "Galaxy S21",
            "price": 800,
            "brand": "Samsung"
        }
    }
}

# ...
# router
```

### 定義 Schema
在 FastAPI 中，我們可以透過 `schema` 來定義 `Body` <br>
一般我們都會建立 `schemas` 的資料夾，並根據 `router` 來分類 <br>

而 `schemas` 的 `User` class <br>
同樣要繼承 `pydantic` 的 `BaseModel` <br>
並依據 `User` 的 `schema` 來定義 <br>
```python
from datetime import date

from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str
    email: str
    birthday: date
```

同樣的，我們也可以在 `schemas` 中定義 `Item` <br>
```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float
    brand: str
```


完成後的目錄結構如下 <br>
```
schemas
├── items.py
└── users.py
```

## FastAPI 中的 Body

接下來我們就可以在 `router` 中使用 `schemas` 來定義 `Body` <br>
在 `main.py` 中引入剛剛定義的 `schemas` <br>
```python
# from fastapi import FastAPI

# from setting.config import get_settings
# 引入剛剛定義的 schemas !
from schemas.users import User as UserSchema
from schemas.items import Item as ItemSchema

# fake_db 
# ... 

```

再更新我們的 API <br>
- users
```python
@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    if user_id not in fake_db["users"]:
        return {"error": "User not found"}
    return {"user": fake_db['users'][user_id], "query": qry }

@app.post("/users")
def create_users(user: UserSchema):
    fake_db["users"][user.id] = user
    return user
```
- items
```python
@app.get("/items/{item_id}")
def get_items_without_typing(item_id, qry):
    if item_id not in fake_db["items"]:
        return {"error": "Item not found"}
    return {"item": fake_db['items'][item_id], "query": qry }

@app.post("/items")
def create_items(item: ItemSchema):
    fake_db["items"][item.id] = item
    return item
```

## 測試

先到 Swagger UI 看一下 create user 的 API <br>
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day05/user-create-ui.png)

接著我們可以點選 `Try it out` 來測試 <br>
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day05/user-create-try.png)

create user 的結果
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day05/user-create-result.png)

使用 get user 的 API 來看一下 <br>
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day05/user-get.png)
可以看到我們剛剛新增的 user 已經在 fake_db 中了 <br>

## 總結

使用 **schema** 可以確保我們的資料符合我們的預期 ( 因為 `pydantic` 會幫我們驗證 ) <br>
而透過 schema 產生的 Swagger UI 也可以幫助我們測試 API <br>
也可以很清楚的看到 API 要帶入的 Body 格式 <br>
在前端開發時，可以很方便的參考 Swagger UI 來開發 <br>

## 那如果想要設定 API 的 response 的 schema 呢？

我們會在明天的文章中談到 <br>
如何設定 API 的 response 的 schema <br>
