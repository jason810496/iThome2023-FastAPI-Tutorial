## [[Day29]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day29) FastAPI : Refactoring & CROS 

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day29 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day29)** <br>
## Reference 

- [twtrubiks : postgresql master slave video tutorial](https://www.youtube.com/watch?v=zxxzcpvCa6o&ab_channel=%E6%B2%88%E5%BC%98%E5%93%B2)
- [twtrubiks : postgresql note - master slave](https://github.com/twtrubiks/postgresql-note/tree/main/pg-master-slave)
- [System design paradigm: Primary-replica pattern](https://luanjunyi.medium.com/system-design-paradigm-primary-replica-pattern-dc621bf195f1)
- [postgresql replication](https://editor.leonh.space/2023/postgresql-replication/)
- [mysql : master slave](https://medium.com/dean-lin/%E6%89%8B%E6%8A%8A%E6%89%8B%E5%B8%B6%E4%BD%A0%E5%AF%A6%E4%BD%9C-mysql-master-slave-replication-16d0a0fa1d04)

## 前言

在一系列的文章中，我們多新增 `Cache` 和 `Primary-Replia` 架構 <br>
今天會再進行最後的 `Refactoring` <br>
並且說明 `CORS` 的細節 <br>
和 `Monitoring` 的概念 <br>


## Config Setting 

我們可以再進一步優化上次的 `get_settings` ( 會回傳當前的環境變數設定 )  <br>
上次為了 `Primary-Replica` 架構，我們多新增 `get_primary_replica_setting` <br>

<br>

但是這會 **增加 CRUD 的相依性** ! <br>
如果之後要測試不同的架構或載入不同環境，就須多寫 `get_a_setting` 、 `get_b_setting` ... <br>
也需要對所有有需要載入環境變數的檔案，**都要做修改** <br>

## Decopuling Config Setting

### Decopuling ? 
**Decopuling** : **解耦** <br>
> 代表把程式之間的 **相依性** 降到最低 <br>
> 程式之間的 **相依性** 越低，程式的 **彈性** 越高 <br>

<br>

良好的**解耦** 應該要可以讓我們切換不同的架構、不同的 Databases 時
都不需要修改程式碼 <br>
只需要從外部載入不同的設定檔，就可以達到切換的效果 <br>

### Decopuling Config Setting 實作

所以我們可以讓 `get_settings` 針對目前的環境，回傳不同的設定 <br>
而不是讓使用不同設定的程式，去呼叫不同的 `get_a_setting` 、 `get_b_setting` ... <br>

<br>

這邊一樣列出多個 Setting Class ，不過讓 `get_settings` 根據 `APP_MODE` 這個環境變數來回傳不同設定 <br>

```python
import os
from functools import lru_cache

class BaseSettings():
    # ...

class DevSettings(BaseSettings):
    # ...

class ProdSettings(BaseSettings):

class PrimaryReplicaSettings(BaseSettings):
    # ...

@lru_cache()
def get_settings() -> BaseSettings:
    if os.getenv("APP_MODE") == "DEV":
        return DevSettings()
    elif os.getenv("APP_MODE") == "PROD":
        return ProdSettings()
    elif os.getenv("APP_MODE") == "PRIMARY-REPLICA":
        return PrimaryReplicaSettings()
    else:
        raise ValueError("Invalid APP_MODE")
```

<br>

經過改寫 <br>
不論當前的環境是什麼，我們都可以透過 `get_settings` 來取得當前的設定 ！<br>

## Decopuling Database Injections

之前我們將 `Primary-Replica` 架構實作放在 `/database/primary_replica.py` 中 <br>
雖然我們同樣將 Database Injection 命名成 `crud_class_decorator` <br>

<br>

但是因為原本 `crud_class_decorator` 是放在 `/database/generic.py` 中 <br>
這會造成在 CRUD 時，需要從**不同檔案**中 import `crud_class_decorator` <br>

<br>

所以我們可以額外新增加 `/database/injection.py` <br>
來處理 `crud_class_decorator` 的相依性 <br>

```python
@lru_cache()
def crud_class_decorator(cls):
    if settings.app_mode == "PRIMARY-REPLICA":
        # [Note]
        from .primary_replica import crud_class_decorator as primary_replica_crud_class_decorator
        return primary_replica_crud_class_decorator(cls)
    
    curd_cls_dec_dict = {
        "MYSQL":generic_crud_class_decorator,
        "POSTGRESQL":generic_crud_class_decorator,
    }

    return curd_cls_dec_dict[settings.db_type](cls)
```

<br>

這樣無論使用什麼架構、什麼資料庫 <br>
都可以透過 import `/database/injection` 的 `crud_class_decorator` 來做使用！ <br>

## Database Dependency 的 Import 時機

先觀察一下 <br>
我們在 `/database/injection.py` 中 <br>
import `primary_replica_crud_class_decorator` 和 `generic_crud_class_decorator` 的時機 <br>

<br>

如果也將 import `primary_replica_crud_class_decorator` 和 `generic_crud_class_decorator` 寫在檔案最上方時 <br>
這會 Database connection 錯誤 <br>
> 例如：目前要跑 `DEV` 架構 <br>
> <br>
> `/database/injection` 會從 `/database/primary_replica` 中 import `primary_replica_crud_class_decorator` <br>
> <br>
> 但是我們也將 `create_engine` 寫在 `/database/primary_replica` 中 <br>
> 這造成 **我們沒有提供 Primary-Replica 的 Database connection 的必要參數** 但是卻要建立 Primary-Replica 的 Database connection <br>

<br>

所以 **先確認當前的環境**，再 import 需要的 Database dependency <br>
就可以避免這個問題 <br>

## CORS

### What is CORS ?

**CORS** : Cross-Origin Resource Sharing , 跨來源資源共用 <br>
瀏覽器的一個機制，用來防止跨網域的攻擊 <br>

<br>

例如：我們的 frontend 是在 `https://frontend.com` <br>
但是我們的 backend 是在 `https://backend.com` <br>
我們可以在 backend 的 response header 中，加入 `Access-Control-Allow-Origin: https://frontend.com` <br>
這樣瀏覽器就會知道，這個 response 是可以被 `https://frontend.com` 存取的 <br>

<br>

如果 `https://frontend-test.com` 沒有加入 `Access-Control-Allow-Origin` <br>
那麼瀏覽器就會拒絕 `https://frontend-test.com` 存取 `https://backend.com` 的資源 <br>

<br>

需要注意的是，**如果是在不同的 port** <br>
也會被視為不同的網域 <br>

### CORS in FastAPI

在 FastAPI 中，我們可以透過 `fastapi.middleware.cors` 來實作 CORS <br>

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    # "http://localhost:5137",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

可以將要允許的網域寫在 `origins` 陣列中 <br>
> 尤其是在 production 環境中 <br>
> 要記得將我們 frontend 的 domain 加到 `origins` 中 ! <br>

<br>

### CROS 實驗

我們這邊先將 `http://localhost:5137` 註解掉 <br>
先建立測試的 frontend <br>

<br>

`/frontend/run.py`

```python
import uvicorn  

if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=5137,reload=True)
```
我們將 frontend 跑在 5137 port <br>
<br>

`/frontend/app.py`

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/",response_class=HTMLResponse)
async def root():
    return '''
    <html>
        <head>
            <title>Frontend</title>
        </head>
        <body>
            <h1>Test Frontend Fetch</h1>
            <p>Enter the route of the backend to fetch data from:</p>
            <input id="url" value="/api/users" />
            <button onclick="fetchData()">Fetch Data</button>
            <pre id="result"></pre>
            
            <script>
                async function fetchData() {
                    const url = 'http://localhost:8001' + document.getElementById('url').value;
                    const response = await fetch(url);
                    const data = await response.text();
                    document.getElementById('result').innerText = data;
                }
            </script>
        </body>
    '''
```

![frontend]()

這邊我們在 frontend 中加上一個 input 和 button <br>
當我們輸入 backend 的 route 後並按下 button 後 <br>
會 `fetch` 來打 backend 的 API <br>

<br>

接著我們同時跑 backend 和 frontend 來進行 CORS 實驗 <br>

<br>

![run fontend backend]()

### 不加入 origins

剛剛已經先將 `http://localhost:5137` 從 `origins` 中註解掉 <br>

<br>

![cors error]()

而我們在 frontend 中輸入 `/api/users` 後 <br>
可以看到 CORS 的錯誤訊息 <br>

### 加入 origins

接著我們將 `http://localhost:5137` 加回 `origins` 中 <br>

<br>

![cors success]()

這樣就可以正常的 fetch backend 的 API 了 <br>

## 總結

今天我們將 Config 和 Database 做重構 <br>
將 `get_settings` 和 `crud_class_decorator` 的相依性降到最低 <br>
可以直接透過載入不同的設定檔，來達到切換不同架構、不同資料庫的效果 <br>
不需要修改程式碼 ！<br>

<br>

最後我們也說明了 CORS 的概念 <br>
也一個簡單的實驗來測試 CORS 的效果 <br>



## Reference

- [FastAPI : CORS](https://fastapi.tiangolo.com/tutorial/cors/)
