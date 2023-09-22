# [Day10] 連接 Database

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day10 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day10)** <br>

## 連接 Database

今天終於要來連接 Database 了 ! <br>
這邊會同時使用 [PostgreSQL](https://www.postgresql.org/) 和 [MySQL](https://www.mysql.com/) 作為我們的 Database <br>
這邊會使用 [Docker](https://www.docker.com/) 來建立我們的 Database <br>
在 CRUD 的部分，我們會使用 [SQLAlchemy](https://www.sqlalchemy.org/) 來幫助我們操作 Database <br>

## Requirement

<!-- - `databases` : 一個支援多種 Database 的套件 -->
- `sqlalchemy` : Python 的 ORM 套件
- `psycopg2-binary` : PostgreSQL 的 Python 連接套件
- `PyMySQL` : MySQL 的 Python 連接套件

```bash
poetry add psycopg2
poetry add PyMySQL
poetry add sqlalchemy
```

## 建立 Database

我們使用 `Docker` 來建立我們的 Database <br>
關於 `Docker` 的安裝與使用，可以參考 [Docker docs](https://docs.docker.com/get-started/) <br>
> 因為 `Docker` 的 loading 足夠再講一個鐵人賽 <br>
> 所以就不在這邊多做介紹了 <br>

### PostgreSQL

```bash
docker run --name fastapi_postgres_dev -e POSTGRES_USER=fastapi_tutorial -e POSTGRES_PASSWORD=fastapi_tutorial_password -e POSTGRES_DB=fastapi_tutorial -p 5432:5432 --volume fastapi_tutorial_postgres_dev:/var/lib/postgresql/data -d postgres:15.1 
```

### MySQL

```bash
docker run --name fastapi_mysql_dev -e MYSQL_USER=fastapi_tutorial -e MYSQL_ROOT_PASSWORD=fastapi_tutorial_password -e MYSQL_DATABASE=fastapi_tutorial -p 3306:3306 --volume fastapi_tutorial_mysql_dev:/var/lib/mysql -d mysql:8.1
```

> 這邊的 `fastapi_tutorial_postgres_dev` 和 `fastapi_tutorial_mysql_dev` 是用來持久化 Container 資料的 Volumn <br>
> 就算把 Container 刪除，再次綁定這個 Volumn 時
> 資料還是會存在 !<br>

### 檢查 Database 是否建立成功

```bash
docker ps
```
![docker ps](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day10/docker-ps.png)

或是使用 docker desktop 來檢查
![docker desktop](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day10/docker-desktop.png)

## 連接 Database

### Database connection url & Engine

在初始化 `sqlalchemy` 時，需要用到 `create_engine` 來建立 Database 的連接 <br>
而 `create_engine` 的參數中，需要傳入 Database 的連接 url <br>
也可以透過 `url_object` 創建 <br>

database url 的格式如下 : <br>
```bash
TYPE://USERNAME:PASSWORD@HOST:PORT/DATABASE
TYPE+DRIVER://USERNAME:PASSWORD@HOST:PORT/DATABASE # 如果需要指定 driver
```

透過 database url 來使用 `create_engine` <br>
```python
from sqlalchemy import create_engine

engine = create_engine("postgresql://fastapi_tutorial:fastapi_tutorial_password@localhost:5432/fastapi_tutorial")
```

或是透過 `engine.URL` 創建 `url_object` 來使用 `create_engine` <br>
```python

from sqlalchemy import create_engine
from sqlalchemy.engine import URL

url_object = URL(
    drivername="postgresql",
    username="fastapi_tutorial",
    password="fastapi_tutorial_password",
    host="localhost",
    port=5432,
    database="fastapi_tutorial",
)

engine = create_engine(url_object)

# ...
```


### `sessionmaker`

在使用 `sqlalchemy` 時，我們會透過 `sessionmaker` 來建立 `session` <br>
而 `sessionmaker` 的參數中，是使用剛剛創建的 `engine` <br>
並且可以設定 ORM 的參數，如 `autocommit` 和 `autoflush` <br>


```python
# ....
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# ....
```

## 完整設定

### 更改 `.env` 

在 `setting/.env.dev` 中，新增相對應 Database 的 url <br>
```bash
POSTGRESQL_DATABASE_URL='postgresql://fastapi_tutorial:fastapi_tutorial_password@localhost:5432/fastapi_tutorial'
MYSQL_DATABASE_URL='mysql+pymysql://root:fastapi_tutorial_password@localhost:3306/fastapi_tutorial'
```
要注意的是 MySQL 的 url 中，user 的部分是 **`root`**<br>

### 更改 `run.py`

在 `run.py` 中 <br>
新增 `--db <option>` 來指定要使用的 Database ， 預設是用 PostgreSQL <br>
並且將 `--db <option>` 的值，存到環境變數 `DB_TYPE` 中 <br>
```python
if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Run the server in different modes.")
    # 將 parser.add_argument 的部分，分成不同的 group
    # 原本的改為 app_mode
    app_mode = parser.add_argument_group(title="App Mode", description="Run the server in different modes.")
    app_mode.add_argument("--prod",action="store_true", help="Run the server in production mode.")
    app_mode.add_argument("--test",action="store_true", help="Run the server in test mode.")
    app_mode.add_argument("--dev",action="store_true", help="Run the server in development mode.")

    # 新增 db_type
    db_type =  parser.add_argument_group(title="Database Type", description="Run the server in different database type.")
    db_type.add_argument("--db", help="Run the server in database type.",choices=["mysql","postgresql"], default="postgresql")

    # ...


    # export DB_TYPE 環境變數
    os.environ["DB_TYPE"] = args.db
```

### 更改 `setting/config.py`


因為跟剛在 `run.py` 中新增 `DB_TYPE` 環境變數 <br>
所以在 `setting/config.py` 中可以透過載入 `DB_TYPE` 來動態的載入對應的 Database url <br>
```python
class Settings():
    # ...
    # 多新增 db_type
    db_type:str = os.getenv("DB_TYPE").upper()
    database_url: str = os.getenv(f"{db_type}_DATABASE_URL")
```

### 新增 `database/generic.py`

因為剛剛透過環境變數 `DB_TYPE` 來動態的載入對應的 Database url <br>
所以我們只需要新增一個 `database/generic.py` <br>
作為所有 Databases 通用的 ORM 設定檔 <br>
> 剛剛 `run.py` 、 `setting/condig.py` 和 `database/generic.py` 的設定
> 可以避免我們為了不同的 Database 而需要新增不同的 ORM 設定檔 <br>
> 原本需要寫 `database/postgresql.py` 、 `database/mysql.py` 和 `databases/xxx.py` <br>
> 現在只需要寫 `database/generic.py` <br>

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from setting.config import get_settings


settings = get_settings()


engine = create_engine(
    settings.database_url ,
    echo=True,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    return SessionLocal()
```

## 更新 `api/infor.py`

在 `api/infor.py` 中，我們會透過 `get_db` 來取得 `session` <br>
在 `/infor` API endopint : 
```python
from sqlalchemy import text # 新增 text

from database.generic import get_db # 新增 get_db

# ...

@router.get("/infor")
def get_infor():

    databases = None
    db_session = get_db()
    
    try :
        databases = db_session.execute(text("SELECT datname FROM pg_database;")).fetchall()
    except Exception as e:
        print(e)

    if databases is None:
        try :
            databases = db_session.execute(text("SHOW DATABASES;")).fetchall()
        except Exception as e:
            print(e)

    return {
        # ....
        "db_type": settings.db_type,
        "database_url": settings.database_url,
        "database": str(databases)
    }
```

因為 `postgresql` 和 `mysql` 的 `SHOW DATABASES` 的語法不同 <br>
所以這邊我們使用 `sqlalchemy` 的 `text` 來幫助我們執行原生的 SQL 語法 <br>
> 這邊只是為了示範，所以沒有做任何 SQLI 的保護 <br>

## 測試

以預設的 PostgreSQL 來起 server : 
```bash
poetry run python3 run.py   
```
![default server](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day10/default-server.png)

再改以 MySQL 來起 server : 
```bash
poetry run python3 run.py --db mysql
```

![mysql server](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day10/mysql-server.png)

可以看到 `db_type` 和 `database_url` 都有改變 <br>
而回傳的 `databases` 也根據我們用的 DB 有不同 <br>

## 總結

今天我們學習了如何連接 Database <br>
並且透過 `sqlalchemy` 來幫助我們操作 Database <br>
並透過 argument parser 來動態的載入對應的 Database url <br>
和使用所有 SQL DB 通用的 ORM 設定檔 <br>

> 明天才會開始講 SQLAchemy 的 model 和
> SQLAchemy 的初步CRUD <br>


#### Reference

- [Docker with PostgreSQL](https://hub.docker.com/_/postgres)
- [Docker with MySQL](https://hub.docker.com/_/mysql)
- [SQLAlchemy : create_engine](https://docs.sqlalchemy.org/en/14/core/engines.html#sqlalchemy.create_engine)
- [SQLAlchemy : database urls](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls)