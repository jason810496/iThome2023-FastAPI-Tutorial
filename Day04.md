# [Day04] FastAPI 基礎架構

## 我們昨天做了什麼？
> [ 昨天的 branch ](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day03)
> 我們把 `uvicorn` 包裝成 `run.py` ，並且加上 `.env` 方便設定環境變數
> 可以直接透過 `python run.py --<mode>` 來啟動 FastAPI
> 但我們還沒有講解 `main.py` 中 FastAPI 到底做了什麼事情 ！

## FastAPI 基礎架構

在昨天的 `main.py` 中，我們其實只有做兩件事情
- 建立 FastAPI app 的 instance
- 定義 API
    - HTTP method
    - Python Typing
    - Path parameter Typing
    - Query parameter Typing


### 建立 FastAPI app

`app` 是一個 FastAPI 的 instance，我們可以由這個 instance 中定義我們所有的 API <br>
並且 `uvicorn` 也是透過 import 這個 instance 來啟動 server <br>
```python
from fastapi import FastAPI

app = FastAPI()
```

### 定義 API

如果有寫過 `express` 或是 `flask` 的朋友，應該對這個語法不陌生 <br>
`@app.get("/")` 這個 decorator 代表這個 function 會來處理進入 `/` 的 `GET` request <br>

```python
@app.get("/")
def hello_world():
    return "Hello World"
```

而另一段 
```python
@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    return {"user_id": user_id, "query": qry }
```
代表這個 function 會來處理進入 `/users/{user_id}` 的 `GET` request <br>
並且 `user_id` 是一個 `path parameter` ， `qry` 是一個 `query parameter`

### API HTTP method

除了 `get` 之外，如果要使用其他 HTTP method ，可以使用以下的語法
- `@app.post("/route")`
- `@app.put("/route")`
- `@app.delete("/route")`
- `@app.patch("/route")`
- `@app.HTTP_METHOD("/route")` ...etc

### Python Typing

在 FastAPI 中，了解 Python Typing 是非常重要的一環 <br>
( 會是使用 `Typing` 可以說已經會 50% FastAPI 了 )

#### Python 內建的 Typing

> 可以在 [Day04 : syntax_review/typing.py]() 中看到範例

我們先來看一下為 Python function 加上 Typing 的好處 <br>
先來看一些範例 : <br>
```python
def add(x, y):
    return x + y

def merge(a, b):
    return f"{a} with {b}"

def insert(user , db ):
    return db.insert(user)
```

以 `add` 來說，我們可以看到這個 function 的功能是將兩個變數相加 <br>
但 `x`和 `y` 可能是 `int` `str` `float` 甚至是 `list` <br>
而 function 的定義很簡單，所以我們用起來不太會有問題

<br>

但是來看一下 `insert` 這個 function ，我們可以看到這個 function 的功能是將 `user` insert 到 `db` 中 <br>
但我們看不出來 `user` 是 `dict` `class` `list` 還是 `str` <br>
同樣的 `db` 可能是 `session` `connection` `class` 等<br>
在沒有加上 `typing` 的情況下，我們容易在使用這個 function 的時候出錯

<br>

- 在 function 的入參數加上 Typing <br>
    可以透過 `<var_name> : <type>` 來定義 
- 在 function 的回傳值加上 Typing <br>
    可以透過 `<fun_name> -> <type>` 來定義 <br>

加上 Typing 後的 function 如下 : <br>
```python
def add(x: int, y: int) -> int:
    return x + y

def merge(a: str, b: str) -> str:
    return f"{a} with {b}"

def insert(user: dict , db: Session) -> None:
    return db.insert(user)
```

### FastAPI Router Typing

在 FastAPI 中，我們可以透過 `typing` 來定義 API function 中 <br>
`path parameter` 、 `query parameter`的型別 <br>

我們先來比較一下有沒有加上 Typing 的差別<br>
```python
# 有加上 Typing
@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    return {"user_id": user_id, "query": qry }

# 沒有加上 Typing
@app.get("/items/{item_id}")
def get_items_without_typing(item_id, qry):
    return {"item_id": item_id, "query": qry }
```

啟動 FastAPI 後，看一下 Swagger UI <br>
![user](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/user.png)
可以看到 `user_id` 是一個 `int` ， `query` 是一個 `str` <br>
如果我們 `user_id` 是用 `string` 在 Swagger UI 中會報錯 <br>
![user ui error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/user-ui-error.png)
如果是使用 `curl` 來呼叫 API 會回傳 `422 Unprocessable Entity` <br> 
![user 422](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/user-422.png)
我們可以在 `response` 中看到 `detail` 中有 `msg` 代表 `user_id` 應該要是 `int` <br>
能夠及時在定義 `router` 的時候就發現這個問題 ！

![item](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/item.png)
可以看到 `item_id` 和 `query` 並沒有特別說型態 <br>
當我們在接完 DB 之後的測試階段才遇到報錯 <br>
就會**很難 Debug** 了 ！

### Optional Query parameter

再次觀察剛剛兩個 API 的 Swagger UI 和 code<br>
![user](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/user.png)
![item](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/item.png)

user : 
```python
@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    return {"user_id": user_id, "query": qry }
```

item : 
```python
@app.get("/items/{item_id}")
def get_items_without_typing(item_id, qry):
    return {"item_id": item_id, "query": qry }
```

可以看到 user 的 query parameter 有 ` = None` ，但 item 的 query parameter 沒有 <br>   
這代表 item 的 query parameter 是必填的，但 user 的 query parameter 可以不填 <br>
如果 item 的 query parameter 不填也會報 `422 Unprocessable Entity` <br>
![item without para](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/main/assets/Day04/item-without-para.png)

## Json 入參 ?

剛剛加上的 Typing 是用來定義 `path parameter` 和 `query parameter` 的型別 <br>
那如果我們想要定義 `request body` 的型別呢 ？ <br>
我們會在明天談到 FastAPI 中由 `pydantic`提供 <br>
另一個也很重要的概念： **Schema** ！




