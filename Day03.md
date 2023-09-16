
# [Day03] FastAPI 設定與 Uvicorn 包裝

**本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day03 branch]()** <br>

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
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day03/uvicorn-start.png)

接著打開瀏覽器，輸入 `http://localhost:5002` <br>
可以看到 Swagger UI 的介面
![](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day03/swagger.png)

我們會在明天再細講 FastAPI 的架構

## 透過 uvicorn 來 serve FastAPI

現在我們可以透過 `uvicorn main:app --reload --host 0.0.0.0 --port 5002` <br>
但每次都要打這麼長的指令，有點麻煩 <br>
所以我們可以把 `uviorn` 包裝成 `.py`
再加上 `.env` 方便設定環境變數
> 其實主要是為了之後 **database connect url** 設定 ！

## 包裝 uvicorn + fastapi


包裝完成後的目錄結構如下：
```
.
├── main.py
├── run.py
└── setting
    ├── .env.dev
    ├── .env.prod
    ├── .env.test
    └── config.py
```
可以參考 [FastAPI Tutorial : Day03]() 的 branch

### /setting

建立 `/setting` 目錄 <br>
各個 mode 的 `.env` 設定檔案 <br>
以及 `config.py` 作為需要環境變數的 dependency <br>
```bash
mkdir setting
touch setting/.env.{dev,prod,test}
touch setting/config.py
```

`.env` 檔案內容如下：

- `.env.dev`
```bash
APP_MODE='dev'
PORT=8001
RELOAD=True
DATABASE_URL='dev_database'
```

- `.env.test`
```bash
APP_MODE='test'
PORT=8002
RELOAD=False
DATABASE_URL='test_database'
```

- `.env.prod`
```bash
APP_MODE='prod'
PORT=8003
RELOAD=False
DATABASE_URL='prod_database'
```



引入 `config.py` 需要的套件 <br>
```python
import os
from functools import lru_cache

from dotenv import load_dotenv


@lru_cache()
def get_settings():
    load_dotenv( f".env.{os.getenv('APP_MODE')}")
    return Settings()
```

建立 `Settings` 物件 <br>
```python
class Settings():
    app_name:str = "iThome2023 FastAPI Tutorial"
    author:str = "Jason Liu"

    app_mode: str = os.getenv("APP_MODE")
    port:int = int(os.getenv("PORT"))
    reload:bool = bool(os.getenv("RELOAD"))
    database_url:str = os.getenv("DATABASE_URL")
```

因為等一下會在 `run.py` 中設定 `APP_MODE` 環境變數 <br>
所以我們可以透過 `os.getenv('APP_MODE')` 載入相對應的 `.env` 檔 <br>


```python
@lru_cache()
def get_settings():
    load_dotenv( f".env.{os.getenv('APP_MODE')}")
    return Settings()
```

不過會遇到一個問題，就是每次需要環境變數時都需要跑一次 `load_dotenv()` 和 `os.getenv()` <br>
所以我們可以透過 `@lru_cache()` 來做一個簡單的 cache <br>
只有在第一次跑到 `get_settings()` 時才會去載入 `.env` 檔案，接下來都會從 cache 回傳 `Setting()` 的 instance <br>
可以參考一下圖片 <br>

![lru cache with setting object](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day03/lru-cache.png)

( 截自 [FastAPI Advanced setting : creating the settings only once with lru_cache](https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru_cache) )

### run.py

建立 `run.py` <br>
```bash
touch run.py
```

在 `run.py` 中加入以下的 code <br>
先引入會用到的套件
```python
import argparse
import os

from dotenv import load_dotenv
import uvicorn
```
- `argparse` : 用來解析 command line 的參數
- `os` 和 `dotenv`: 用來取得 `.env` 檔的環境變數
- `uvicorn` : 這次包裝成 `.py` 之後就可以直接使用 `run.py` 來啟動 FastAPI 而不用以 `uvicorn main:app --reload --host <host> --port <port>` 來啟動


接著我們要來解析 command line 的參數 <br>
```python
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    parser.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    parser.add_argument("--test",action="store_true", help="Run the server in test mode.")
    parser.add_argument("--dev",action="store_true", help="Run the server in development mode.")
    
    args = parser.parse_args()
```
現在就能夠以 `python run.py --dev` 讓 FastAPI 以 development mode 啟動 <br>
以 `python run.py --prod` 讓 FastAPI 以 production mode 啟動 <br>


接著我們要來取得分別取得 `.env` 檔案中的環境變數 <br>
可以透過 `load_dotenv()` 來載入 `setting/.env.*` 檔案中的環境變數 <br>
並利用 `os.getenv()` 來取得環境變數 <br>
```python
    if args.prod:
        load_dotenv("setting/.env.prod")
    elif args.test:
        load_dotenv("setting/.env.test")
    else:
        load_dotenv("setting/.env.dev")

    uvicorn.run("main:app", host="0.0.0.0" , port=int(os.getenv("PORT")) , reload=bool(os.getenv("RELOAD")) )
```

## main.py

最後我們要來修改 `main.py` <br>
先從 `setting/config.py` 中引入 `get_settings()` <br>
```python
from setting.config import get_settings
```


加上 `/infor` 的測試 API 回傳目前載入的 setting <br>
```python
@app.get("/infor")
def get_infor():
    settings = get_settings()
    return {
        "app_name": settings.app_name,
        "author": settings.author,
        "app_mode": settings.app_mode,
        "port": settings.port,
        "reload": settings.reload,
        "database_url": settings.database_url
    }
```

## 測試

現在我們可以分透過 `--<mode>` 讓 FastAPI 載入不同設定檔<br>

- development mode
加上 `--dev`
```bash
python run.py --dev
```
執行結果
![start server in dev mode](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day03/start-server-dev.png)

以 `curl` 測試 `/infor` API
```bash
curl http://localhost:8001/infor
```
`curl` 的結果
```
{"app_name":"iThome2023 FastAPI Tutorial","author":"Jason Liu","app_mode":"dev","port":8001,"database_url":"dev_database","reload":"True"}
```

- production mode
加上 `--prod`
```bash
python run.py --prod
```

執行結果
![start server in prod mode](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day03/start-server-prod.png)

以 `curl` 測試 `/infor` API
```bash
curl http://localhost:8003/infor
```

`curl` 的結果
```
{"app_name":"iThome2023 FastAPI Tutorial","author":"Jason Liu","app_mode":"prod","port":8003,"database_url":"prod_database","reload":"False"}
```


##### Reference 

[FastAPI : Advanced setting](https://fastapi.tiangolo.com/advanced/settings/)
[FastAPI : Creating the settings only once with lru_cache](https://fastapi.tiangolo.com/advanced/settings/#creating-the-settings-only-once-with-lru_cache)
[Python argparse](https://docs.python.org/3/library/argparse.html)
[python-dotenv](https://pypi.org/project/python-dotenv/)
[lru_cache](https://docs.python.org/zh-tw/3/library/functools.html)




