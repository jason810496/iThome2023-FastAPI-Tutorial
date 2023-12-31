# [Day01]  FastAPI 推坑與框架的朋友們

## 本系列文章目錄

在 30 天的鐵人賽，我們會完成了以下的內容 <br>

### 基礎功能
- FastAPI 基本用法 : 以 FastAPI 來實作基本 RESTful API
- Databse Injections : 以 SQLAlchemy 作為 ORM 來操作資料庫
- 以 Pytest 撰寫 Unit Test 和 Benchmark
- 以 Docker + Docker Compose 來部署專案

### 架構實作
- OAuth2 + JWT 實作 : 以 OAuth2 + JWT 來實作登入機制
- 以 Redis 作為 Server Side Cache : 實作 Key-Value Cache 和 Pagenation Cache 
- 實作 Primary Replica 架構 : 以 Read-Write Splitting 和 Read-Only Replica 來提升 Query 效能
- 實作 Event Driven 架構 : 以 Celery + Redis 作為 Message Broker 來實作非同步任務
- 實作 Rate Limit Middleware : 以 Redis 作為 Rate Limit 的資料儲存

**在 Day01 ~ Day09 : 介紹 FastAPI 的基本用法** <br>
- [[Day01]  FastAPI 推坑與框架的朋友們](https://ithelp.ithome.com.tw/articles/10320028)
- [[Day02] FastAPI 啟動： 環境安裝](https://ithelp.ithome.com.tw/articles/10320376)
- [[Day03] FastAPI 設定與 Uvicorn 包裝](https://ithelp.ithome.com.tw/articles/10320570)
- [[Day04] FastAPI 基礎架構](https://ithelp.ithome.com.tw/articles/10322582)
- [[Day05] FastAPI : Schema & Pydantic](https://ithelp.ithome.com.tw/articles/10322585)
- [[Dat06] FastAPI : Response model](https://ithelp.ithome.com.tw/articles/10324121)
- [[Day07] 再談 Python Typing 與 Schema 常見錯誤](https://ithelp.ithome.com.tw/articles/10324964)
- [[Day08] 為 Swagger (OpenAPI) 加上更多資訊](https://ithelp.ithome.com.tw/articles/10325684)
- [[Day09]  架構優化：依據項目切分 Router](https://ithelp.ithome.com.tw/articles/10326343)

**在 Day10 ~ Day16 : 在 FastAPI 中使用 SQLAlchemy 和 Depends injection** <br>
- [[Day10] 連接 Database](https://ithelp.ithome.com.tw/articles/10326759)
- [[Day11] SQLAlchemy Model](https://ithelp.ithome.com.tw/articles/10328525)
- [[Day12] 使用 SQLalchemy](https://ithelp.ithome.com.tw/articles/10329028)
- [[Day13] 架構優化： Depends 萬用刀 & 常見錯誤](https://ithelp.ithome.com.tw/articles/10329960)
- [[Day14] 架構優化：將 CRUD 與 API endpoint 分離](https://ithelp.ithome.com.tw/articles/10331002)
- [[Day15] 架構優化：非同步存取 DB](https://ithelp.ithome.com.tw/articles/10331531)
- [[Day16] 架構優化：非同步存取 DB （2）](https://ithelp.ithome.com.tw/articles/10332377)

**在 Day17 ~ Day20 : 實作 OAuth2 + JWT 登入機制** <br>
- [[Day17] OAuth2 實例： 密碼驗證](https://ithelp.ithome.com.tw/articles/10333002)
- [[Day18] OAuth2 實例： OAuth2 Schema & JWT](https://ithelp.ithome.com.tw/articles/10333835)
- [[Day19] OAuth2 實例：Authorize Dependency 、 權限管理](https://ithelp.ithome.com.tw/articles/10333926)
- [[Day20] OAuth2 實例：實作總結](https://ithelp.ithome.com.tw/articles/10335041)

**在 Day21 ~ Day23 : 以 Pytest 來撰寫 Unit Test 和 Docker Compose 來部署專案** <br>
- [[Day21] Pytest 入門與安裝](https://ithelp.ithome.com.tw/articles/10335690)
- [[Day22] 測試： Pytest `paramaterize` 與功能驗證](https://ithelp.ithome.com.tw/articles/10336272)
- [[Day23] 部署： 透過 Docker Compose 部署 FastAPI + PostgreSQL + MySQL](https://ithelp.ithome.com.tw/articles/10336829)

**在 Day24 ~ Day26 : 以 Redis 實作 Server Side Cache** <br>
- [[Day24] 架構優化 : Redis Cache , `redis-py` 架構初探](https://ithelp.ithome.com.tw/articles/10337357)
- [[Day25] 架構優化 : Redis 實作 Server Cache](https://ithelp.ithome.com.tw/articles/10337853)
- [[Day26] 架構優化 : Redis Pagenation Cache 實作](https://ithelp.ithome.com.tw/articles/10338413)

**在 Day27 ~ Day29 : 實作 Primary Replica 架構** <br>
- [[Day27]  FastAPI : Primary Replica 架構實作](https://ithelp.ithome.com.tw/articles/10338649)
- [[Day28] FastAPI : Primary Replica 架構實作 (2)](https://ithelp.ithome.com.tw/articles/10339203)
- [[Day29] FastAPI : Refactoring & CROS 設定](https://ithelp.ithome.com.tw/articles/10339634)
- [[Day30] FastAPI 系列：山重水複疑無路，柳暗花明又一村](https://ithelp.ithome.com.tw/articles/10340054)

**在 Day31 ~ Day33 : Event Drive 與 Rate Limit 實作** <br>
> 來不及在 iThome 鐵人賽關版前寫完的文章 <br>
> 都會放放在 [Github Repo](https://github.com/jason810496/iThome2023-FastAPI-Tutorial) 上，有興趣的可以自行閱讀 ! <br>
- [[Day31]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day31) : Event Driven 初探(1) 以 Redis 作為 Message Queue
- [[Day32]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day32) : Event Driven 初探(2) 以 Celery + Redis 作為可監控式 Message Broker
- [[Day33]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day33) 以 Redis 實作 Rate Limit Middleware

<br>

希望這些內容可以幫助到大家! <br>
也歡迎大家提出建議和指教 🙌

---
> 以下是 Day1 正文！

FastAPI 是由 ：
- [Starlette](https://www.starlette.io/)
- [Pydantic](https://docs.pydantic.dev/latest/)

這兩個框架作為基礎搭建的

## FastAPI 優點

### 速度快
#### django / flask / FastAPI 大比拼

- 在 [web framework benchmark](https://web-frameworks-benchmark.netlify.app/result?asc=0&f=fastapi,django,flask&metric=percentile50&order_by=level64) 中查詢這三個框架的比較，可見 FastAPI 比 django / flask 快上約 5 ~ 10 倍
    - 在 Request / Second 的圖表：
        ![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day01/comparison-req-sec.png)
    - 在 Average Latency 的圖表：
        ![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day01/comparison-avg.png)

### 內建支援 async function

並且 FastAPI 支援 `async` function
```python
@app.get("/async")
async def async_hello_world():
    return "Hello World"

@app.get("/sync")
def sync_hello_world():
    return "Hello World"
```


### 內建支援 OpenAPI (Swagger) 規範
跑起 FastAPI 後，可以在 `http://localhost:port/docs` 看到 Swagger UI <br>
在開發初期測試時非常方便！

![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day01/swagger-ui.png)

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
        - [FastAPI-users](https://github.com/fastapi-users/fastapi-users)
        - [FastAPI-redis-cache](https://github.com/a-luna/fastapi-redis-cache)
        - [FastAPI-auth](https://github.com/dmontagu/fastapi-auth)
        - [FastAPI-security](https://github.com/jacobsvante/fastapi-security)

##### reference

- [FastAPI document](https://fastapi.tiangolo.com/)
- [web-frameworks-benchmark](https://web-frameworks-benchmark.netlify.app/result?asc=0&f=fastapi,django,flask&metric=totalRequestsPerS&order_by=level64)
- [fastapi-the-good-the-bad-and-the-ugly](https://dev.to/fuadrafid/fastapi-the-good-the-bad-and-the-ugly-20ob)