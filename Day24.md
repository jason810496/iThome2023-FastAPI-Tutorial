## [Day24] 架構優化: Redis Cache , `redis-py` 架構初探

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day23 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day23)** <br>

## 前言

在前面的章節中，我們已經完成了一個基本的 `FastAPI` 專案，並且透過 `Docker Compose` 來部署 Backend 與 DB <br>

<br>

在接下來的文章 <br>
我們將會透過 `Redis` 來實作一個 Server Cache <br>
並且將 Cache 與 CRUD 進行整合，讓我們的 API 更加的快速 <br>

<br>

今天會先寫一些 `redis-py` 的基本用法測試 <br>
讓我們知道可以如何透過 `redis-py` 來實作我們的 Cache <br>

## 關於 Redis

`Redis` 是一個開源的 `in-memory` 資料庫<br>
它支援多種資料結構，例如 `string` , `hash` , `list` , `set` , `sorted set` 等等 <br>
可以用來當作 `cache` , `message broker` , `queue` ... <br>

<br>

要在 `Python` 中使用 `Redis` ，我們可以透過 `redis-py` 來實作 <br>

```bash
poetry add redis
```

如果要使用 `async` 版本的 `redis` <br>
只需要從 `redis.asyncio` 中 import `Redis` 即可 <br>

```python
from redis.asyncio import Redis
```

> 原本有 [`aioredis`](https://github.com/aio-libs-abandoned/aioredis-py) 這個套件，但是在 `v4.2.0+` 後已經被整合到 `redis-py` 中 <br>
> 可以直接以 `redis.asyncio` 來使用 <br>

## 連接 Redis

### Redis Server
先用 Docker 來啟動一個 Redis Server <br>
並設定密碼為 `fastapi_redis_password` <br>

```bash
docker run --name fastapi_redis_dev -p 6379:6379 -d  redis:7.2.1 --requirepass "fastapi_redis_password"
```

可以再額外安裝 [`redis Insight`](https://redislabs.com/redis-enterprise/redis-insight/) 來檢視我們的 Redis Server <br>

<br>

![redis insight 1](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day24/redis-insight-1.png)
( Redis Insight 首頁 ) <br>

![redis insight 2](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day24/redis-insight-2.png)
( Redis Insight 中的 Key List ) <br>

![redis insight password](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day24/redis-insight-password.png)
( 第一次連的時候要記得在右側設定密碼 ) <br>

### Redis Connection

可以將接下來的測試程式碼寫在 `tests/test_redis.py` 中 <br>
而我們的 `REDIS_URL` 會是 `redis://:fastapi_redis_password@localhost:6379` <br>

```bash
touch tests/test_redis.py
touch tests/test_redis_async.py
touch tests/test_redis_om.py
```

<br>

`tests/test_redis.py` <br>
```python
import redis

REDIS_URL = "redis://:fastapi_redis_password@localhost:6379"
```

<br>

而 `redis-py` 的連線方式有兩種: <br>
1. 透過 `Redis` 類別來建立連線
`tests/test_redis.py` <br>
```python
def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)

    value = 'bar'
    redis_connection.set('foo', value )
    result = redis_connection.get('foo')
    redis_connection.close()

    assert result.decode() == value
```
這種方式會在每次操作完後自動關閉連線 <br>

<br>

2. 建立 Connection Pool 來管理連線
`tests/test_redis.py` <br>
```python
# ...
connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

# ...

def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=connection_pool)

    value = 'bar2'
    redis_connection.set('foo2', value )
    result = redis_connection.get('foo2')
    redis_connection.close()

    assert result.decode() == value
```
這種方式則是透過 `ConnectionPool` 來管理連線 <br>
可以在每次操作完後，不用關閉連線，而是將連線放回 `ConnectionPool` 中 <br>

<br>

接著可以透過 `pytest` 來測試 redis 連線 <br>
```bash
poetry run pytest tests/test_redis.py
```

![pytest redis](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day24/pytest-redis.png)
( 可以看到測試通過 ) <br>
可以看到測試通過 <br>

也可以在 `redis insight` 中看到我們剛剛新增的 `foo` 與 `foo2` <br>
![redis insight 3](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day24/redis-insight-3.png)
( 可以看到剛剛設定的 `foo:bar` 和 `foo2:bar2` ) <br>

## Redis Async Connection

`async` 版本的 `redis` 連線方式與 `sync` 版本的方式相同 <br>
一樣由 `Redis` 類別與 `ConnectionPool` 來管理連線 <br>

<br>

差別是 `redis.asyncio` 中的 `Redis` 的操作都是 `async` 的 <br>
所以要使用 `await` 來取得結果 <br>

`tests/test_redis_async.py` <br>
```python
import pytest
import redis.asyncio as redis # <--- 注意這邊是使用 redis.asyncio

REDIS_URL = "redis://:fastapi_redis_password@localhost:6379"

@pytest.mark.asyncio
async def test_redis_connection():
    redis_connection = redis.Redis.from_url(REDIS_URL)
    value = 'bar_async'
    await redis_connection.set('foo_async', value )
    result = await redis_connection.get('foo_async') # <--- 要使用 await 來取得結果
    redis_connection.close()

    assert result.decode() == value
```

透過 Connection Pool 來管理連線的方式也是一樣的 <br>

`tests/test_redis_async.py` <br>
```python
# ...

connection_pool = redis.ConnectionPool.from_url(REDIS_URL)

# ...
@pytest.mark.asyncio
async def test_redis_connection_pool():
    redis_connection = redis.Redis(connection_pool=connection_pool)
    
    value = 'bar_async2'
    await redis_connection.set('foo_async2', value)
    value = await redis_connection.get('foo_async2')
    redis_connection.close()

    assert value.decode() == 'bar_async2'
```

## Redis Object Mapper

`redis-py` 也提供了 `Object Mapper` 的功能 <br>
讓我們可以直接將 `Object` 存入 `Redis` 中 <br>
可以透過 `redis-om-py` 來實作 <br>

<br>

```bash
poetry add redis-om
```

<br>

`redis-om` 的操作方式與 `SQLAlchemy` 類似 <br>
都是需要先定義 Data Model <br>

<br>

`tests/test_redis_om.py` <br>
```python
import pytest
from redis_om import get_redis_connection

REDIS_URL = "redis://:fastapi_redis_password@localhost:6379"

redis = get_redis_connection(url=REDIS_URL)
```
在 `redis-om` 中，我們需要透過 `get_redis_connection` 來取得 `redis` 的連線 <br>

<br>

接著我們可以定義一個 `UserReadCache` 的 Data Model <br>
而 `redis-om` 有提供:
- `HashModel` 來讓我們可以將 `Object` 存成 `Hash` <br>
- `JsonModel` 來讓我們可以將 `Object` 存成 `JSON` <br>

`tests/test_redis_om.py` <br>
```python
# ...
from typing import Optional
from redis_om import HashModel , Field

# ...


class UserReadCache( HashModel ):
    id: int = Field(index=True)
    name : str = Field(index=True)
    email: str = Field(index=True)
    avatar:Optional[str] =  None

    class Meta:
        database = redis
```


## Reference

- [redis py github](https://github.com/redis/redis-py)
- [async redis python example](https://redis-py.readthedocs.io/en/stable/examples/asyncio_examples.html)
- [use redis](https://blog.csdn.net/wgPython/article/details/107668521)
- [redis client setup example](https://github.com/tiangolo/fastapi/issues/1694)
- [redis developer : fastapi example](https://github.com/redis-developer/fastapi-redis-tutorial/blob/master/app/main.py)
- [flask with redis-om example](https://redis.io/docs/clients/om-clients/stack-python/)
- [fastapi redis cache setting](https://juejin.cn/post/6974299485983735822)