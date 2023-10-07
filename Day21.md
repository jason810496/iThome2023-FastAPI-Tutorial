# 測試：[Day21] Pytest 入門與安裝

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day21 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day21)** <br>

## 前言

我們從 [Day17](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day17) 到 [Day20](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day20) 完成整個 Oauth2 實例的實作 <br>
<br>

今天會進入 **測試** 的章節 <br>
我們會使用與 FastAPI 整合很好的 `pytest` 來進行測試 <br>

## 安裝

我們先為專案安裝 `pytest` 與 `pytest-sugar` 這兩個套件 <br>
前者是測試框架，後者是讓測試結果更好閱讀的套件。

再加上 `pytest-asyncio` 這個套件，讓我們可以在測試中使用 async function <br>
而 `httpx` 則是用來模擬 http request 的套件 <br>

```bash
poetry add pytest
poetry add pytest-asyncio
poetry add httpx
poetry add pytest-sugar
```


## 建立測試目錄

先建立一個 `tests` 目錄 <br>
並加上一下初始檔案 <br>

```bash
mkdir tests
touch tests/__init__.py
touch tests/pytest.ini
touch tests/conftest.py
touch tests/app.py
touch tests/test_user.py
```

### pytest.ini

`pytest.ini` 是 `pytest` 的設定檔 <br>
可以讓我們在執行 `pytest` 時，自動帶入一些參數 <br>

```ini
[pytest]
addopts = -v --disable-warnings
```

- `-v` : 顯示詳細的測試結果
- `--disable-warnings` : 關閉警告訊息

### conftest.py

`conftest.py` 是 `pytest` 中一個特殊的檔案 <br>
可以讓我們在測試中使用一些共用的設定 <br>

<br>

我們原先跑 server 的 `run.py` 中 <br>
有加上 `argparse` 的設定來選擇要跑哪個環境、PORT、DB 等等 <br>
在 `conftest.py` 中，我們也可以加上 arguments 的設定 <br>

<br>

`tests/conftest.py`
```python
def pytest_addoption(parser):
    parser.addoption("--prod",action="store_true", help="Run the server in production mode.")
    parser.addoption("--test",action="store_true", help="Run the server in test mode.")
    parser.addoption("--dev",action="store_true", help="Run the server in development mode.")
    parser.addoption("--sync",action="store_true", help="Run the server in Sync mode.")
    parser.addoption("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")
```

只需要在 `conftest.py` 中的 `pytest_addoption` 中 <br>
為 `parser` 加上我們需要的 arguments <br>
就可以透過 `pytest` 的 `--help` 來看到這些 arguments <br>

```bash
poetry run pytest --help
```

![custom-arguments](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day21/custom-arguments.png)

## 建立測試用的 FastAPI app

因為我們原先的 FastAPI app 是在 `main.py` 中 <br>
不是在 `tests` 目錄中 <br>
如果照樣 import `main.py` 來使用 FastAPI app <br>
會跳出 

```
ImportError: attempted relative import beyond top-level package
```
的錯誤 <br>

<br>

所以我們需要在 `tests` 目錄中建立一個 `app.py` <br>
作為測試用的 FastAPI app <br>

### 載入環境變數

與原本 `main.py` 一樣，我們需要載入環境變數 <br>
剛剛我們在 `conftest.py` 中加入了 `--prod`、`--test`、`--dev` 這三個 arguments <br>
那我們要如何在 `pytest` 中使用這些 arguments 呢？ <br>

<br>

我們可以透過 `pytest` 的 **`request`** 來取得這些 arguments <br>
並使用 `request.config.getoption` 來取得 arguments 的值 <br>

<br>

`tests/conftest.py`
```python
import os 
import pytest_asyncio
from dotenv import load_dotenv

@pytest_asyncio.fixture(scope="session")
async def dependencies(request):
    args = request.config

    if args.getoption("prod"):
        load_dotenv("../setting/.env.prod")
    elif args.getoption("test"):
        load_dotenv("../setting/.env.test")
    else:
        load_dotenv("../setting/.env.dev")

    if args.getoption("sync"):
            os.environ["RUN_MODE"] = "SYNC"
    else:
        os.environ["RUN_MODE"] = "ASYNC"

    os.environ["DB_TYPE"] = args.getoption("db")
    print("DB_TYPE",os.getenv("DB_TYPE"))
```
這邊因為是使用 `async` function <br>
所以需要使用 `pytest_asyncio` 來建立 **`fixture`** <br>

> [How to pass arguments in `pytest` by command line ?](https://stackoverflow.com/questions/40880259/how-to-pass-arguments-in-pytest-by-command-line#answer-53383793)

## `pytest` 中的 `fixture`

`pytest` 中的 `fixture` 可以讓我們在測試中共用一些資源 <br>
> 有點像是 FastAPI 中的 `Depends` <br>
> 都有一點 Dependency Injection 的感覺 <br>
> [`pytest` : `fixture` quick example](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#quick-example)

<br>

`pytest` 中的 `fixture` 有這幾種 scope <br>
- `function` : 每個測試都會執行一次
- `class` : 每個測試類別都會執行一次
- `module` : 每個測試 module 都會執行一次
- `session` : 整個測試會執行一次

<br>

而剛剛的 `dependencies` 就是一個 `session` scope 的 `fixture` 例子 <br>
因為只會在 **建立測試 FastAPI App 實例**的時候才會載入環境變數 <br>
要在其他 `fixture` 中使用 `dependencies` <br>
只需要在 function 的參數中加入 `dependencies` 就可以了 <br>

```python
@pytest_asyncio.fixture(scope="session")
async def dependencies(request):
    # ...


async def test_that_require_dependencies(dependencies):
    # ...
    os.getenv("DB_TYPE")
```
以這個例子來說 <br>
在 `test_that_require_dependencies` 這個測試 <br>
使用 `os.getenv("DB_TYPE")` 就可以取得 `dependencies` 中載入的環境變數 !<br>

### 在 `pytest` 中使用 `async` function

但是如果直接跑剛剛的測試 <br>
會跳出以下的錯誤 <br>

```
Failed: ScopeMismatch: You tried to access the function scoped fixture event_loop with a session scoped request object, involved factories:
```

<br>

在 `pytest` 中，如果要支援 `async` function <br>
除了要使用 `pytest_asyncio` 來建立 `fixture` <br>
如果 `pytest_asyncio.fixture` 的 scope 是 `session` <br>
還需要在 `conftest.py` 中加上以下的設定 <br>

<br>

`tests/conftest.py`
```python
# ...
import pytest
import asyncio


# ...

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()
```

> [using module with pytest mark asyncio](https://stackoverflow.com/questions/56236637/using-pytest-fixturescope-module-with-pytest-mark-asyncio#answer-56238383)

## `pytest` 入門

在 `pytest` 中 <br>
如果要建立一個測試 <br>
必須將:
- 檔名以 `test_` 開頭
- function 名稱以 `test_` 開頭
- class 名稱以 `Test` 開頭

<br>

在 test function 中 <br>
以 **`assert`** 來判斷測試是否通過 <br>

<br>

`tests/test_user.py`
```python

def user():
    assert 1 == 1

def test_user():
    assert 1 == 1
```
用 `pytest` 執行這個測試 <br>

<br>

```bash
poetry run pytest
```

![pytest first run](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day21/pytest-first-run.png)

會看到 `pytest` 會自動找到 `tests` 目錄中以 `test_` 開頭的 .py 檔<br>
並執行這些檔案中以 `test_` 開頭的 function <br>

### 在 `pytest` 中共享 `fixture`

接著我們要先建立測試用的 FastAPI app 的 module level `fixture`<br>
並且要先載入 `dependencies` fixture <br>
可以把會使用的 `fixture` 都定義在 `conftest.py` 中 <br>

<br>

`tests/conftest.py`
```python
# ...
from httpx import AsyncClient

# ...

@pytest_asyncio.fixture(scope="module")
async def async_client(dependencies) -> AsyncClient:
    from .app import app
    async with AsyncClient(app=app,base_url="http://test") as client:
        yield client
```

而特別將 `import .app` 放在 `async_client` 的 function body 中 <br>
是因為要先等 `dependencies` 這個 `fixture` 先載入環境變數後 <br>
才能正確的建立 FastAPI app 實例 <br>

### 使用 `async_client` fixture

接著就可以在 `test_user.py` 中使用 `async_client` 這個 `fixture` <br>

`tests/test_user.py`
```python

async def test_get_users(async_client):
    response = await async_client.get("api/users")
    assert response.status_code == 200
```

但是會發現顯示 `skipped` <br>
![pytest skipped](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day21/pytest-skipped.png)

### 使用 `mark.asyncio` decorator

這是因為 `pytest` 預設是不支援 `async` function 的 <br>
如過要使用 `async` test function <br>
必須使用 `@pytest.mark.asyncio` 來特別標記 <br>

<br>

`tests/test_user.py`
```python
@pytest.mark.asyncio
async def test_users(async_client):
    response = await async_client.get("/api/users")
    assert response.status_code == 200 
```

![first passed](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day21/first-passed.png)

可以看到 `test_users.py` 中的 `test_get_users` 通過了測試! <br>

## 總結

今天我們學習了如何使用 `pytest` 來進行測試 <br>
也學習了如何在 `pytest` 中使用 `async` function <br>
以及如何在 `pytest` 中使用 `fixture` <br>

<br>

明天我們會建立 mock user 來進行測試 <br>
並學習如何使用 `parametrize` 來帶入不同測試資料 <br>

## Reference

- [test setup](https://testdriven.io/blog/fastapi-crud/#test-setup)
- [How to pass arguments in `pytest` by command line ?](https://stackoverflow.com/questions/40880259/how-to-pass-arguments-in-pytest-by-command-line#answer-53383793)
- [`pytest` : Quick start fixture & fixture scope](https://docs.pytest.org/en/7.1.x/how-to/fixtures.html#fixture-scopes)
- [pytest fixture scope](https://pytest-with-eric.com/pytest-advanced/pytest-fixture-scope/)
- [using module with pytest mark asyncio](https://stackoverflow.com/questions/56236637/using-pytest-fixturescope-module-with-pytest-mark-asyncio)

