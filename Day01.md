# [Day01]  FastAPI 推坑與框架的朋友們

FastAPI 是由 ：
- [Starlette](https://www.starlette.io/)
- [Pydantic](https://docs.pydantic.dev/latest/)

這兩個框架作為基礎搭建的

## FastAPI 優點

### 速度快
#### django / flask / FastAPI 大比拼

- 在 [web framework benchmark](https://web-frameworks-benchmark.netlify.app/result?asc=0&f=fastapi,django,flask&metric=percentile50&order_by=level64) 中查詢這三個框架的比較，可見 FastAPI 比 django / flask 快上約 5 ~ 10 倍
    - 在 Request / Second 的圖表：
        ![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Day01/assets/Day01/comparison-req-sec.png)
    - 在 Average Latency 的圖表：
        ![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Day01/assets/Day01/comparison-avg.png)


### 內建支援 OpenAPI (Swagger) 規範
跑起 FastAPI 後，可以在 `http://localhost:port/docs` 看到 Swagger UI <br>
在開發初期測試時非常方便！

![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Day01/assets/Day01/swagger-ui.png)

### 內建型別檢查

**如果喜歡 `TypeScript` 那一定也會喜歡 `FastAPI`**

在 
- API endpoint 的輸入參數或輸出參數
- endpoint 與 CRUD 之間的傳遞

都可以透過 `Schema` 作為型別檢查的基礎 <br>
而 `Schema` 就是由 `Pydantic` 所提供的 `BaseModel`  繼承而來<br>
如下面的例子：
```python
from datetime import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    id: int
    name: str
    country: str
    age: int

class UserCreate(UserBase):
    address: str
    birthday: datetime
    password: str

class UserPubic(UserBase):
    pass

class UserPricate(UserBase):
    address: str
    birthday: datetime
    password: str

```

讓我們在寫 `FastAPI` 時，會有寫 `TypeScript` 的既視感
> FastAPI 之於 其他 python 後端框架架，就像 typescript 之於 javascript (單指的是語法層面)


## Summary


FastAPI 的優點：
- 速度快
    - 比 django / flask 快上約 5 ~ 10 倍
    - 支援 async / await
- 內建支援 OpenAPI (Swagger) 規範
    - 在開發初期測試時非常方便！
- 內建型別檢查
    - 有 `TypeScript` 的感覺
- 容易測試
    - 有提供 `TestClient` ，並可以透過 `pytest` 進行測試
- 豐富文件與社群
    - [FastAPI document](https://fastapi.tiangolo.com/) 提供許多教學與範例
    - 也有許多人整合 FastAPI 與其他套件，例如：
        - [FastAPI-redis-cache](https://github.com/a-luna/fastapi-redis-cache)
        - [FastAPI-auth](https://github.com/dmontagu/fastapi-auth)
        - [FastAPI-security](https://github.com/jacobsvante/fastapi-security)

##### reference

- [FastAPI document](https://fastapi.tiangolo.com/)
- [web-frameworks-benchmark](https://web-frameworks-benchmark.netlify.app/result?asc=0&f=fastapi,django,flask&metric=totalRequestsPerS&order_by=level64)
- [fastapi-the-good-the-bad-and-the-ugly](https://dev.to/fuadrafid/fastapi-the-good-the-bad-and-the-ugly-20ob)