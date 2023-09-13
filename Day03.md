# [Day03] FastAPI 設定與 Uvicorn 包裝

在[昨天]()把基本 FastAPI 的環境安裝好 <br>
今天要來做一些基本的設定，並且把 FastAPI 包裝成一個可以直接執行的檔案

## FastAPI 啟動 !

將以下 code 貼到 `main.py` 中

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return "Hello World"

@app.get("/users/{user_id}")
def get_users(user_id: int, qry: str = None):
    return {"user_id": user_id, "query": qry }
```

接者可以在 terminal 中執行以下指令 <br>
來啟動 FastAPI 並且開在 5002 port 當有改動到時會 hot reload
```shell
uvicorn main:app --reload --host 0.0.0.0 --port 5002
```

應該會看到以下的結果
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Day03/assets/Day03/uvicorn-start.png)

接著打開瀏覽器，輸入 `http://localhost:5002` <br>
可以看到 Swagger UI 的介面
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Day03/assets/Day03/swagger.png)

我們會在明天再細講 FastAPI 的架構

## 透過 uvicorn 來 serve FastAPI

現在我們可以透過 `uvicorn main:app --reload --host 0.0.0.0 --port 5002` <br>
但每次都要打這麼長的指令，有點麻煩 <br>
所以我們可以把 `uviorn` 加上 `.env` 並且包裝成一個可以直接執行的檔案
> 主要是為了之後 database connect url 設定

## 包裝 uvicorn + fastapi

先安裝 `pydantic-settings` 這個套件
```shell
poetry add pydantic-settings
```




##### Reference 

[FastAPI : Advanced setting](https://fastapi.tiangolo.com/advanced/settings/)


## 我們剛剛做了什麼？

### 建立 FastAPI app

`app` 是一個 FastAPI 的 instance，我們可以在這個 instance 中定義我們所有的 API
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

#### 支援 async function

並且 FastAPI 支援 `async` function ，也可以將這個 function 定義成 `async`
```python
@app.get("/")
async def hello_world():
    return "Hello World"
```

#### API HTTP method

除了 `get` 之外，如果要使用其他 HTTP method ，可以使用以下的語法
- `@app.post("/route")`
- `@app.put("/route")`
- `@app.delete("/route")`
- `@app.patch("/route")`