## [[Day32]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day32) Message Queue 初探(2) : 以 Celery + RabbitMQ 作為可監控式 Worker Message Queue

##  前言

我們在 [Day31](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day31) 以 `redis` 作為 Message Queue 來進行非同步任務的執行 <br>

<br>

昨天是以 `STT` (Speech To Text) 作為範例 <br>
今天我們將會以 **影像辨識** ( 這邊使用 `YOLO` ) 作為範例 <br>
> 但 `YOLO` 的部分我們不會特別去介紹 <br>

<br>

並且使用 `RabbitMQ` 作為 Message Queue 來進行非同步任務的執行 <br>
再搭配 `Flower` 來監控 `RabbitMQ` 的狀態 <br>

## Redis vs RabbitMQ

Redis 和 RabbitMQ 都可以作為 Message Queue <br>
但是還是有一些差異 <br>

### Redis

Redis 畢竟本質是 `in-memory` 的 database <br>
預設是不會對資料進行 **持久化** 的 <br>

<br>

因為每個操作都是原子性的 <br>
又提供如 `list` 、 `set` 、 `sorted set`、`hash` 等資料結構 <br>
所以可以作為 Message Queue 來使用 <br>
但是在 **處理容錯** 時需要在 **業務邏輯** 中進行處理 <br>

<br>

> 雖然可以為 Redis 設定  <br>
> AOF (Append Only File) 或 RDB (Redis Database File) <br>
> 來進行持久化 <br>
> 但由 config 的策略不同，還是有可能導致資料丟失 <br>
> 而設定高頻率的持久化也會導致 Redis 效能下降 <br>

### RabbitMQ

而 RabbitMQ 則是專門用來處理 Message Queue 的 <br>
在處理 **容錯** 時可以透過 `RabbitMQ` 本身的機制來進行處理 <br>
它可以透過 `ACK` 來確保訊息的傳遞 <br>
也可以為傳輸過程中的訊息進行 **持久化** <br>
本身還提供 Pub/Sub 、 Routing 、 Topic 、 RPC 等功能 <br>

### 總結

Redis 和 RabbitMQ 都可以作為 Message Queue <br>
可以依照需求來選擇使用 <br>

<br>

如: 在確保資料正確性的前提下 <br>
使用 **RabbitMQ** 來作為 Message Queue 會比較好 <br>

<br>

又如果: 在處理 **即時性** 的資料 <br>
使用 **Redis** 來作為 Message Queue 會比較好 <br>


> - [Medium : Redis vs RabbitMQ](https://medium.com/@contact_45426/redis-vs-rabbitmq-a-detailed-comparison-998ed1ba7fc2)
> - [AWS : Redis vs RabbitMQ](https://aws.amazon.com/tw/compare/the-difference-between-rabbitmq-and-redis/)
> - [知乎 : Redis vs RabbitMQ](https://zhuanlan.zhihu.com/p/41850085)
> - [RDB vs AOF](https://hackmd.io/@KaiChen/S1Bj9dgm9)


## Celery 和 Flower

Celery 是一個 Python 的非同步任務佇列/任務調度器 <br>
可以使用 `Redis` 和 `RabbitMQ` 作為 Message Queue <br>

<br>

Celery 本身提供了一個 `Flower`( Web UI 介面 ) 來監控 Celery 的狀態 <br>
可以透過 `Flower` 來監控 `RabbitMQ` 的狀態 <br>

<br>

### Celery 和 Flower 安裝

只需要透過 `pip` 來安裝即可 <br>
```bash
pip install celery
pip install flower
```

### Celery Broker

Broker 是 Celery 用來接收任務的 Message Queue ( Message Broker ) <br>
Celery 支援多種 Message Broker <br>
如: `RabbitMQ` 、 `Redis` 、 `Amazon SQS` 、 `MongoDB` 、 `Kafka` 等 <br>

### Celery Backend

Backend 是 Celery 用來 **儲存任務結果** 的設定 <br>
可以使用 `Redis` 和其他 `Database` 或 ORM 來作為 Backend <br>
如: `SQLAlchemy` 、 `Django ORM` 、 `MongoDB` 、 `Cassandra` 等 <br>
甚至可以使用 `RPC` 、`S3`或 `filesystem` 來作為 Backend <br>

> [celery result backend 列表](https://docs.celeryq.dev/en/stable/userguide/configuration.html#std-setting-result_backend)

### Celery Worker

Celery Worker 是 Celery 用來執行任務的 process instance <br>
可以透過 `celery multi` 來啟動多個 Celery Worker <br>
需要透過 Celery App Instance 的 `task` **decorator** 來註冊任務 <br>



### Celery

基本的 Celery 設定如下 <br>
`/celery_tasks/celery_app.py` <br>
```python
from __future__ import absolute_import, unicode_literals
from celery import Celery
import os

app = Celery(
    "rmq",
    broker=os.environ.get("CELERY_BROKER_URL", "amqp://guest@localhost//"),
    backend=os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
    include=["celery_tasks.tasks"],
    result_expires=60,
)

if __name__ == "__main__":
    app.start()
```

- `include` : Celery Task 的 import path
- `result_expires` : Celery Task 的結果過期時間

### Celery Task

Celery Task 的設定如下 <br>
`/celery_tasks/tasks.py` <br>
```python   
from __future__ import absolute_import, unicode_literals
from celery_tasks.celery_app import app
from celery import subtask

@app.task
def add(x, y):
    import time
    time.sleep(5)
    return x + y

@app.task
def crawler(url: str):
    import requests
    res = requests.get(url)
    return res.json()

@app.task(bind=True)
def bind_task(self, x, y):
    task_id = self.request.id
    return {"task_id": task_id, "result": x + y}

@app.task
def callback_task(x, y):
    import time
    time.sleep(5)
    subtask("celery_tasks.tasks.crawler").delay("https://httpbin.org/get")
    return x + y
```

可以注意到 <br>
- 如果 task 需要用到其他 module 的話 <br>
    需要在 task 內部 import <br>
- 如果 task 內部需要 **自己的 task id** 的話 <br>
    需要使用 `bind=True` 來設定 <br>
- 如果 task 內部需要 **callback** 的話 <br>
    可以用 `subtask` 來達成 <br>

## 執行 Celery

worker : 
```bash
celery -A celery_tasks.tasks worker -l info
```

flower : 
```bash
celery -A celery_tasks.tasks flower
```


## YOLO 

### reference


## RabbitMQ 設定

這邊我們同樣使用 `docker` 來跑 `RabbitMQ` <br>

```bash
docker run -d --hostname rabbitmq --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

## 


## run command : 

backend : 
```bash
python3 run.py --mq
```

worker : 
```bash
celery -A celery_tasks.tasks worker -l info
```

flower : 
```bash
celery -A celery_tasks.tasks flower
```

frontend : 
```bash
python3 run.py
```

## Reference
- Redis vs Message Queue
    - [Medium : Redis vs RabbitMQ](https://medium.com/@contact_45426/redis-vs-rabbitmq-a-detailed-comparison-998ed1ba7fc2)
    - [AWS : Redis vs RabbitMQ](https://aws.amazon.com/tw/compare/the-difference-between-rabbitmq-and-redis/)
    - [知乎 : Redis vs RabbitMQ](https://zhuanlan.zhihu.com/p/41850085)
    - [RDB vs AOF](https://hackmd.io/@KaiChen/S1Bj9dgm9)

- celery
    - [celery : Getting Started](https://www.celerycn.io/ru-men/celery-chu-ci-shi-yong)
    - [myapollo : python celery](https://myapollo.com.tw/series/python-celery/)
    - [testdriven : fastapi with celery](https://testdriven.io/blog/fastapi-and-celery/)
    
<!-- - [How To Use Server-Sent Events in Node.js to Build a Realtime App](https://www.digitalocean.com/community/tutorials/nodejs-server-sent-events-build-realtime-app)
- [REST API with an asynchronous task queue cluster](https://cloud.tencent.com/developer/article/1943402)
- [install yolo inside docker container](https://lindevs.com/install-yolov8-inside-docker-container-in-linux)
- [Python RabbitMQ 異常重啟機制 Pika重連機制](https://www.jianshu.com/p/60cdc45207cd)  -->