## [[Day27]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day27) FastAPI : Primary Replica 架構實作

> **本次的程式碼與目錄結構可以參考 [FastAPI Tutorial : Day27 branch](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day27)** <br>

## 前言

在 [Day24](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day24) 到 [Day26](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day26) 我們完成 FastAPI + Redis 的 Server Cache 實作 <br>

<br>

今天我們要來實作 FastAPI + PostgreSQL 的 Primary Replica 架構 <br>
Primary Replica 架構: <br>
- 可以優化**查詢**的效能
- `Primary` 負責寫入資料和讀取資料 ( Create, Update, Delete, Read )
- `Replica` 只進行讀取資料 ( Read )
- `Primary` 會與 `Replica` 自動同步資料

<br>

架構圖如下 : <br>

```
  Write  Read
    |     |
    |     ├──------------┐
    |     |              |
    v     v              v
  +------------+   +------------+  
  |   Primary  |   |   Replica  |
  |  Database  |   |  Database  |
  +------------+   +------------+
      |                  ^
      |                  |
      └──-- sync data ---┘
```
> 但我們並不需要在後端同步 Primary 與 Replica 的資料 <br>
> 因為 PostgreSQL 在設定完 Replica 後會自動幫我們同步 <br>

<br>

今天會將 PostgreSQL 的 Replica 環境設定好 <br>
會使用 1 個 Primary 與 1 個 Replica <br>

> Primary-Replica 環境設定都是參考 [twtrubiks : postgresql note - master slave](https://github.com/twtrubiks/postgresql-note/tree/main/pg-master-slave) <br>
> 在 PostgreSQL 中 **只有支援 1 個 Replica** <br>


## Docker Compose 設定

因為 Postgresql 設定 Replica connection 需要使用 IP <br>
所以需要為 service 分被固定的 IP <br>
這邊使用特別為 `network` 加上 `ipam` 的方式來設定 <br>
> `ipam` : IP Address Management <br>
> 可以參考 [Docker Compose : IPAM configuration reference](https://docs.docker.com/compose/compose-file/compose-file-v3/#ipam) <br>
> 並為每個 service 設定 `ipv4_address` 來指定 IP <br>

<br>

`docker-compose-primary-replica.yml`
```yml
services:

  primary:
    # ...
    networks:
      my_network:
        ipv4_address: 172.22.0.100 
# ...
networks:
  my_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.22.0.0/24
          gateway: 172.22.0.1
```

<br>

完整的 `docker-compose-primary-replica.yml` 在： <br>
[`/primary-replica/docker-compose-primary-replica.yml`](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/blob/Day27/docker-compose-primary-replica.yml)


## Primary 設定

### 建立 Replication User

使用 `docker exec -it primary bash` 進入 Primary 的 Container <br>

<br>

可以使用 `psql` 進入 Primary 的 PostgreSQL <br>
進入 PostgreSQL 後下以下指令 <br>
```sql
-- 進入 PostgreSQL
psql -U primary_user -d primary_db

-- 建立 Replication User
CREATE ROLE repuser WITH LOGIN REPLICATION PASSWORD 'repuser_password'; 

-- 查看所有 User
\du
```

![docker exec primary](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/docker-exec-primary.png) <br>
可以看到 `repuser` 已經建立完成，並標示為 `Replication` <br>

### 修改 Primary 的 `pg_hba.conf`

如果有設定好 volume 的話 <br>
應該可以看到 `/db_volumes/primary-replica` 底下有這 4 個目錄 <br>

```
.
├── primary
├── copy
└── replica

4 directories, 0 files
```

![db_volumes primary](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/db_volumes-primary.png) <br> 
在 `primary` 底下可以看到所有 `/var/lib/postgresql/data/` 的資料 <br>
其中有 `postgresql.conf` 與 `pg_hba.conf` 等設定檔案 <br>

<br>

可以直接在本機端修改 `/primary-replica/primary/pg_hba.conf` <br>
在檔案最後加上以下設定 <br>


<br>

`/primary-replica/primary/pg_hba.conf`
```conf
# ...

# Add replication user
host replication repuser 172.22.0.101/32 md5
host replication repuser 172.22.0.102/32 md5
```

<br>

> 也可以直接以 command line 完成 <br>
```
echo "host replication repuser 172.22.0.101/32 md5" >> db_volumes/primary-replica/primary/pg_hba.conf
echo "host replication repuser 172.22.0.102/32 md5" >> db_volumes/primary-replica/primary/pg_hba.conf
```

### 修改 Primary 的 `postgresql.conf`

只需要在 `postgresql.conf` 修改以下幾個設定 <br>

<br>
    
`/primary-replica/primary/postgresql.conf`
```
archive_mode = on
archive_command = '/bin/date'
max_wal_senders = 10
wal_keep_size = 16
synchronous_standby_names = '*'
```

### 加上測試資料

在 Primary Contaienr 中以 `psql` 進入 Postgresql 並加入測試資料<br>
```bash
psql -U primary_user -d primary_db

-- 建立測試資料表
CREATE TABLE test2_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);


-- 插入測試資料
INSERT INTO test_table (name) VALUES ('test1');

-- 列出所有 table
\dt
```

### restart Primary 的 Container

記得要 **restart** Primary 的 Container 來重新載入設定 ！ <br>

## Replica 設定 

### 以 `pg_basebackup` 複製 Primary 的資料

進入 `replica` 的 Container <br>
```bash
docker exec -it replica bash
```

<br>

在 `replica` 底下執行以下指令 <br>
```bash
pg_basebackup -R -D /var/lib/postgresql/copy -Fp -Xs -v -P -h primary -p 5432 -U repuser
```

![pg_basebackup](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/pg_basebackup.png) <br>

### 載入 Primary 的資料

先 **stop** Primary 和 replica 的 Container <br>
```bash
docker stop primary replica
```

<br>

將 `copy` 資料夾複製到 `replica` 的 `data` 資料夾 <br>
```bash
rm -r db_volumes/primary-replica/replica/*
cp -r db_volumes/primary-replica/copy/* db_volumes/primary-replica/replica/
```

再 **restart** Primary 和 Replica 的 Container <br>
```bash
docker compose -f docker-compose-primary-replica.yml restart
```

### 測試 Primary 與 Replica 是否同步運作


先進入 Replica 的 Container <br>
```bash
docker exec -it primary replica
```

<br>

並嘗試進入 PostgreSQL <br>
```bash
psql -U replica_user -d replica_db
```

會發現跳出 Error : <br>
![docker psql replica1 error](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/docker-psql-replica1-error.png) <br>

<br>

嘗試在 `Replica` Contaier 以 `primary_user` 進入 PostgreSQL <br>

![docker replica1 primary_user](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/docker-replica1-primary_user.png) <br>

結果發現可以正常進入 PostgreSQL ! <br>

<br>

我們發現透過 **`pg_basebackup`** 載入備份資料的 Replica database 會變成 Primary database 的 User <br>



### 測試 Primary 與 Replica 是否同步運作

<br>

嘗試在 Primary 的 PostgreSQL 建立一個新的 Table <br>

```bash
docker exec -it primary bash
```

加上 `test2_table` <br>
```sql
-- 進入 PostgreSQL
psql -U primary_user -d primary_db

-- 建立測試資料表 2
CREATE TABLE test2_table (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- 插入測試資料
INSERT INTO test2_table (name) VALUES ('test2');
```

<br>

再進入 Replica 的 PostgreSQL <br>
```bash
docker exec -it replica bash
```

<br>

進入 PostgreSQL <br>
```bash
psql -U primary_user -d primary_db

-- 列出所有 table
\dt
```

![docker replica1 test2_table](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/docker-replica1-test2_table.png) <br>

可以看到 `test2_table` 已經被同步到 Replica 的 PostgreSQL 中 ! <br>

## 修改設定

我們發現透過 **`pg_basebackup`** 載入備份資料的 Replica database 會變成 Primary database 的 User <br>

<br>

所以我們統一將 Primary 與 Replica 都以 `primary-replica/db.env` 來載入設定 

<br>

`/primary-replica/db.env`
```env
POSTGRES_PASSWORD=postgresql_password
POSTGRES_USER=postgresql_user
POSTGRES_DB=postgresql_db
```

這樣就可以避免不同的 User 造成的問題 <br>

# 自動化設定

以上的設定都是手動設定的 <br>
但我們可以透過 shell script 來自動化設定 <br>

<br>

這邊分為 3 個 script : <br>
- `reset.sh` : 重置所有 Container
- `setup.sh` : 設定 Primary 與 Replica
- `test.sh` : 測試 Primary 與 Replica 是否正常運作

<br>

這些 script 都在 [`/primary-replica`](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day27/primary-replica) 底下，這邊也不佔篇幅 <br>

<br>

![primary-replica-copy](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day27/primary-replica-copy.png) <br>

## 總結

今天我們完成了 Primary-Replica 架構中 DB 的設定 <br>
透過 `pg_basebackup` 複製 Primary 的資料到 Replica 中 <br>
並且撰寫 shell script 來自動化設定 <br>

<br>

可以看到在 Primary 中建立的 Table 會自動同步到 Replica 中 <br>

<br>

接下來我們要來實作 FastAPI + PostgreSQL 的 Primary-Replica 架構 <br>
在 CRUD 層面要如何實作 Primary-Replica 架構 <br>


## Reference 

- [twtrubiks : postgresql master slave video tutorial](https://www.youtube.com/watch?v=zxxzcpvCa6o&ab_channel=%E6%B2%88%E5%BC%98%E5%93%B2)
- [twtrubiks : postgresql note - master slave](https://github.com/twtrubiks/postgresql-note/tree/main/pg-master-slave)
- [postgresql replication](https://editor.leonh.space/2023/postgresql-replication/)
- [mysql : master slave](hhttps://medium.com/dean-lin/%E6%89%8B%E6%8A%8A%E6%89%8B%E5%B8%B6%E4%BD%A0%E5%AF%A6%E4%BD%9C-mysql-master-slave-replication-16d0a0fa1d04)