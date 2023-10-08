# [Day23] 部署： 透過 Docker Compose 部署 FastAPI + PostgreSQL + MySQL

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day23 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day23)** <br>

## 完成結果

透過 Docker Compose 一鍵部署 FastAPI + PostgreSQL + MySQL 專案

![docker compose up](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/docker-compose-up.png)

可以任意在 backend Container 中任意切換 DB 進行測試

| ![mysql pytest](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/mysql-pytest.png) | ![postgresql pytest](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/postgresql-pytest.png) |
| :----------------: | :-------------------: |


## 前言

在 [Day21](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day21) 和 [Day23](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day23) 我們完成 `pytest` 的 Unit Test <br>
接下來我們要透過 Docker Compose 來部署我們的 FastAPI 專案 <br>

## Docker Compose 部署

如果單純使用 Docker 部署 FastAPI 專案，我們需要先建立一個給 FastAPI 的 Docker Image <br>
再分別建立 PostgreSQL 和 MySQL 的 Docker Image <br>
最後跑 3 次 `docker run` 來啟動所有 Container <br>

<br>

透過 Docker Compose 我們可以透過一個 `docker-compose.yml` 檔案來定義我們的專案 <br>
並且能一次啟動所有 Container <br>

### FastAPI Docker Image

首先我們先來建立 FastAPI 的 Docker Image <br>
在 `backend` 目錄下建立 `Dockerfile` <br>

```bash
touch backend/Dockerfile
```

由於我們的專案結構是透過 Poetry 來管理的 <br>
所以我們可以先 export Poetry 的 dependencies 到 `backend/requirements.txt` <br>

<br>

```bash
poetry export -f requirements.txt -o backend/requirements.txt
```

<br>

接著就可以開始編寫 `Dockerfile` <br>

`backend/Dockerfile`
```dockerfile
FROM python:3.11.1-slim

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/backend

COPY ./requirements.txt /usr/backend/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /usr/backend/
```

我們把 `workdir` 設定到 `/usr/backend` <br>
特別設定 `PYTHONDONTWRITEBYTECODE` 讓 Python 不會產生 `.pyc` 檔 <br>
可以讓產生的 Docker Image 更小 <br>

### `.dockerignore` 設定

在建立 Docker Image 時，我們可以透過 `.dockerignore` 來避免不必要的檔案被加入 <br>
再次縮小 Docker Image 的大小 <br>

<br>

```bash
touch .dockerignore
```

<br>

`backend/.dockerignore`
```dockerfile
__pycache__
.pytest_cache
Dockerfile
.dockignore
```

這樣在 `COPY . /usr/backend/` 時就不會把這些檔案加入 Docker Image 中 <br>

<br>

與不設定 `.dockerignore` 和 `ENV PYTHONDONTWRITEBYTECODE 1` 時的 Docker Image 大小比較 <br>

| ![small](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/small.png) | ![big](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/big.png) |
| :--------: | :------: |

> 大概小 10MB 左右 <br>
> 影響 Docker Image 大小的因素有很多，像是使用的 Base Image、安裝的套件等等 <br>


### Multi Stage Build

如果一開始的 Poetry 是開在 `backend` 目錄下 <br>
可以在 Build Image 時再產生 `requirements.txt` <br>
並透過 Multi Stage Build 來減少 Image 的大小 <br>

<br>

```dockerfile

FROM python:3.11.1-slim as builder

WORKDIR /tmp

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /tmp/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

FROM python:3.11.1-slim

ENV PYTHONDONTWRITEBYTECODE 1

WORKDIR /usr/backend

COPY --from=builder /tmp/requirements.txt /usr/backend/requirements.txt

# ... 剩下與原本的相同
```

可以參考 [fastapi dockerize : docker image with poetry](https://fastapi.tiangolo.com/deployment/docker/#docker-image-with-poetry)

## 基本 Docker Compose 設定

在根目錄下建立 `docker-compose.yml` <br>

```bash
touch docker-compose.yml
```

<br>

最基本的設定如下 <br>
而 `services` 中的 `backend` 會使用 `backend/Dockerfile` 來建立 Docker Image <br>
PostgreSQL 和 MySQL 則是直接使用 Docker Hub 上的 Image <br>

`docker-compose.yml`
```yml
version: '1.0'

services:
  postgresql_db:
    image: postgres:15.1
    restart: always
    volumes:
      - ./db_volumes/postgresql:/var/lib/postgresql/data/

  mysql_db:
    image: mysql:8.1.0
    restart: always
    volumes:
      - ./db_volumes/mysql:/var/lib/mysql/

  backend:
    build: ./backend
    volumes:
      - ./backend/:/usr/backend/
    command: python3 run.py --prod
    restart: always

networks:
  default: 
    name: fastapi_tutorial_network
```

- `networks` : <br>
這邊我們建立一個 `network` 來讓所有 Container 透過 **Service Name** 來連線 <br>
- `volumes` : 
    - Database : <br>
        這邊我們把 PostgreSQL 和 MySQL 的資料都掛載到 `db_volumes` 目錄下 <br>
        這樣方便我們直接在本機上看到資料 <br>
    - Backend : <br>
        也將目前 `backend` 目錄掛載到 Container 中 <br>
        可以直接在本機上修改程式碼 <br>


### Port

接著我們設定 Database 要 Expose 的 Port <br>
這邊我們設定 PostgreSQL 的 Port 為 `5432` <br>
MySQL 的 Port 為 `3306` <br>

<br>

並將 `backend` Container 的 `8003` Port Forward 到本機的 `8000` Port <br>

`docker-compose.yml`
```yml
version: '1.0'

services:
  postgresql_db:
    # ...
    expose:
      - 5432

  mysql_db:
    # ...
    expose:
      - 3306

  backend:
    # ...
    ports:
      - 8000:8003
```

### Depends On

我們 `backend` Container 會依賴於 PostgreSQL 和 MySQL <br>
應該要先等 Database 啟動完成後才啟動 `backend` <br>

<br>

所以需要特別設定 `depends_on` <br>

`docker-compose.yml`
```yml
# ...
services:
  # ...
  backend:
    # ...
    depends_on:
      - postgresql_db
      - mysql_db
```

## DB env file 設定

### 直接透過 `environment` 設定

對於 PostgreSQL 和 MySQL 我們都需要設定 `environment` <br>
需要將 `POSTGRES_USER`、`POSTGRES_PASSWORD`、`POSTGRES_DB` 這些環境變數在 `docker-compose.yml` 中設定好 <br>

<br>

`docker-compose.yml`
```yml
version: '1.0'

services:
  postgresql_db:
    # ...
    environment:
      - POSTGRES_USER=fastapi_tutorial
      - POSTGRES_PASSWORD=fastapi_tutorial_password
      - POSTGRES_DB=fastapi_tutorial

  mysql_db:
    # ...
    environment:
      - MYSQL_ROOT_PASSWORD=fastapi_tutorial_password
      - MYSQL_DATABASE=fastapi_tutorial
```

這樣的缺點是我們的密碼都會直接寫在 `docker-compose.yml` 中 <br>

### 透過 `env_file` 設定

所以我們可以透過 `env_file` 來設定 <br>
我們先建立要載入的 `.env` 檔案 <br>

<br>

```bash
touch db.{postgresql,mysql}.env
```

<br>

`db.postgresql.env`
```env
POSTGRES_PASSWORD=fastapi_tutorial_password
POSTGRES_USER=fastapi_tutorial
POSTGRES_DB=fastapi_tutorial
```

`db.mysql.env`
```env
MYSQL_ROOT_PASSWORD=fastapi_tutorial_password
MYSQL_DATABASE=fastapi_tutorial
```

<br>

要注意這邊 `.env` 的設定要與 **`backend/setting/.env.prod`** 中的 `DATABASE_URL` 中 **User、Password、DB Name** 一致 <br>

## 修改 `setting/.env.prod` 中的 `DATABASE_URL`

因為我們要透過 Docker Compose 來部署 <br>
有設定 `network` 的關係，所以我們必須要使用 **Service Name** 來連線 <br>
> 有點像 Docker Compose 幫我們設定內網 DNS 的感覺 <br>

要將原本是 `localhost:5432` 的 `DATABASE_URL` 改成 `postgresql_db:5432` <br>
`localhost:3306` 改成 `mysql_db:3306` <br>

<br>

`setting/.env.prod`
```env
# ...

SYNC_POSTGRESQL_DATABASE_URL='postgresql+psycopg2://fastapi_tutorial:fastapi_tutorial_password@postgresql_db:5432/fastapi_tutorial'

ASYNC_POSTGRESQL_DATABASE_URL='postgresql+asyncpg://fastapi_tutorial:fastapi_tutorial_password@postgresql_db:5432/fastapi_tutorial'

SYNC_MYSQL_DATABASE_URL='mysql+pymysql://root:fastapi_tutorial_password@mysql_db:3306/fastapi_tutorial'

ASYNC_MYSQL_DATABASE_URL='mysql+aiomysql://root:fastapi_tutorial_password@mysql_db:3306/fastapi_tutorial'

# ...
```


## 等待 Database Ready

如果這時候直接使用 `docker-compose up` 來啟動 <br>
有時候會發現我們 FastAPI 在連接 Database 時會出現錯誤 <br>
說還無法 connect 到 Database <br>

<br>

這是因為雖然我們有設定 `depends_on` <br>
但是我們的 Database 還沒有啟動完成 <br>

<br>

所以我們可以額外透過 `condition` 和 `healthcheck` 來等待 Database 完全啟動完成 <br>

`docker-compose.yml`
```yml
version: '1.0'

services:
  postgresql_db:
    # ...
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "fastapi_tutorial", "-d", "fastapi_tutorial"]
      interval: 5s
      timeout: 5s
      retries: 5
    # ...
  mysql_db:
    # ...
    healthcheck:
      test: ["CMD", "echo" , ">/dev/tcp/localhost/3306"]
      interval: 5s
      timeout: 5s
      retries: 5
    # ...
```

PostgreSQL 的 `healthcheck` 可以透過 `pg_isready` 來檢查 <br>
MySQL 的 `healthcheck` 則是透過 `echo >/dev/tcp/localhost/3306` 來檢查 <br>

## 測試部署

這時候再直接使用 `docker-compose up` 來啟動 <br>
或是使用 `docker-compose up -d` 來背景執行 <br>

![docker compose final](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/docker-compose-final.png)

就可以看到我們的 FastAPI 專案已經成功部署 <br>
可以在 `localhost:8000/docs` 來看到 Swagger UI <br>

<br>

進入 Backend Container 後 <br>
以 PostgreSQL 測試 <br>

```bash
docker exec -it ithome2023-fastapi-tutorial-backend-1 bash
cd tests && pytest --prod --db postgresql
```

![exec pytest postgresql](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/exec-pytest-postgresql.png)

以 MySQL 測試 <br>

```bash
pytest --prod --db mysql
```

![exec pytest mysql](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day23/exec-pytest-mysql.png)

都可以正常運作 ! <br>

## 總結

今天我們透過 Docker Compose 來部署我們的 FastAPI 專案 <br>
使用 `env_file` 來載入 `db.env` 檔案 <br>
而不用將密碼直接寫在 `docker-compose.yml` 中 <br>

<br>

並且透過 `depends_on`和 `healthcheck` 來等待 Database 完整啟動完成後 <br>
再啟動 `backend` Container <br>

<br>

最後我們進入 `backend` Container 中跑不同 Database 測試 <br>
也可以正常運作 ！<br>

## Reference

- [fastapi dockerize](https://fastapi.tiangolo.com/deployment/docker/)
- [docker compose : wait for postgresql ready using script](https://stackoverflow.com/questions/35069027/docker-wait-for-postgresql-to-be-running#answer-50108745)
- [docker compose : wait for postgresql ready using command](https://stackoverflow.com/questions/35069027/docker-wait-for-postgresql-to-be-running#answer-55835081)
