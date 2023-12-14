## [[Day31]](https://github.com/jason810496/iThome2023-FastAPI-Tutorial/tree/Day31) Message Queue 初探(1) : 以 Redis 作為 Message Queue 執行 Speech Recognition

##  前言

我們先想個情境： <br>
假設我們有 **將音檔轉成文字** 和 **物件偵測** 這些服務 <br>
需要用戶上傳 media file 後，由後端處理 <br>

<br>

但是這些服務 **都需要花費一定的時間** 來處理 <br>
> 可能需要 **數10秒** 或 **數分鐘** 來處理 <br>

<br>

那我們的 Backend API 要如何處理這些服務呢？ <br>

## 流程拆解

STT 的服務可拆解成以下步驟：
1. 上傳 media file
2. 將 media file 轉成 wav file
3. 將 wav file 送到 speech_recognition
4. 回傳 STT 結果

### Speech Recognition
這邊的 **speech_recognition** 是一個 Python 的 library <br>
[pypi : SpeechRecognition](https://pypi.org/project/SpeechRecognition/) <br>

<br>

單跑一次 `sample1.mp4` 的轉檔和 Speech Recognition <br>
大概需要 **11.5** 秒 <br>
![one time stt](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/one-time-stt.png)


<br>

### 建立 API

這邊先建立 `/api/stt.py` <br>
```python
from fastapi import APIRouter 
from fastapi import File, UploadFile
import aiofiles
from uuid import uuid4

from setting.config import get_settings
from jobs.stt import get_text_from_video

settings = get_settings()

router = APIRouter(
    tags=["speech to text"],
    prefix="/stt",
)
```

<br>

並加上印出 response time 的 middleware <br>
`main.py` <br>
```python
def create_message_queue_app():

    app = FastAPI()

    # ...

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next: callable):
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time)
        formatted_process_time = '{0:.4f}'.format(process_time)
        logger.info(f"{request.method} {request.url} {formatted_process_time}s")
        response.headers["X-Process-Time"] = formatted_process_time
        return response
```

![response time middleware](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/response-time-middleware.png)

## Naive Solution

最基本的解法： <br>
將所有事情都丟給同一個 API 去處理 <br>

<br>

`/api/stt.py` <br>
```python
# ...
@router.post("/native")
async def native_processing(file: UploadFile = File(...)):
    save_path = settings.upload_path

    ext_name = file.filename.split(".")[-1]
    hash_name = uuid4().hex[:8]

    out_file_path = f"{save_path}/{hash_name}.{ext_name}"
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    text = get_text_from_video(video_path=out_file_path,uuid=hash_name)

    return {"job_id": hash_name, "text": text}
```
可以看到這個 API 完成了：上傳檔案、轉檔、送到 speech_recognition、回傳結果 <br>
而 `get_text_from_video` 是主要將 media file 轉成 wav file 並送到 speech_recognition 的 function <br>
> 這邊我們先將上傳的檔案存到 local 做 demo <br>
> 實際上應該要存到 S3 或是其他的 storage <br>

<br>

### Benchmark

我們再額外寫一個 muti-process 的 benchmark script <br>
`/tests/mq/parallel_upload.py` <br>
```python
import subprocess
from multiprocessing import Pool
import time

file_name = "sample1.mp4"
url = "http://0.0.0.0:8001/stt/native"

urls = [url for _ in range(5) ]

def upload(url):
    subprocess.call(['curl', '-H', 'Content-Type: multipart/form-data', '-X', 'POST', '-F', f"file=@{file_name};type=video/mp4", url])   

if __name__ == '__main__':
    start = time.time()

    agents = 5
    with Pool(processes=agents) as pool:
        result = pool.map(upload, urls )
    print(result)

    end = time.time()
    print(f"\nTime taken: {end - start}")
```

<br>

執行 `python3 parallel_upload.py` <br>
![native parallel upload](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/native-parallel-upload.png)
> 同時發出 5 個 request，等全部都收到 response 的總時間
可以看到總共花費了快 **50** 秒才收到所有的 response <br>

<br>

由 logging 可以看到 <br>    
一開始的 response time 都是 **20** 秒左右 <br>
但是後面的 response time 都接近 **40 到 50** 秒 <br>
![native response time](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/native-response-time.png)

### 為什麼會這樣？

這是因為以 **Uvicorn** 最為 **FastAPI** 的 server <br>
而 Uvicorn 是以 Muti-threading 的方式來處理 request 的 <br>

<br>

這代表 <br>
當我們發出 request 時，FastAPI 會將這個 request 丟給一個 thread 去處理 <br>
而這個 thread 會一直處理這個 request 直到處理完畢 <br>

<br>

所以當我們發出多個 request 時，會有多個 thread 同時在處理這些 request <br>

<br>

但是這些 thread 都是在同一個 process 裡面 <br>
所以當我們的 CPU 資源不足時，這些 thread 會開始競爭 CPU 資源 <br>

<br>

**這會導我們在處理 CPU bound (需要大量 CPU 資源) 的工作時 <br>
執行效率會變得很差** <br>


## Message Queue

那我們要如何解決這個問題呢？ <br>

<br>

我們可以先將這些 **需要大量 CPU 資源的 job** 都丟到 **message queue** 中 <br>
再由 **worker** 來處理這些 job <br>

<br>

當 worker 處理完畢後 <br>
就可以由後端的 API 撈取結果 <br>


<br>

架構圖如下： <br>
![mq architecture](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/mq-architecture.png)

### 把 job 丟到 message queue 中

後端將「 job 丟到 message queue 」 的實作可以看成 <br>
把一個 message 丟到 message queue 中 <br>
而 message 包含了這個 job 的資訊 <br>
> 以我們的情境來說: 就是 media file 的路徑 <br>
> 以 ML Application 來說: 可能是要跑的 model 和 data resource <br>


### Worker 處理 job

這邊的 **worker** 其實只是一個 **process** <br>
而這些 worker 會從 **message queue** 中取得 job 來處理 <br>
> 由一個完整的 process 來處理一個 job 當然會比由後端的 muti-threading 來處理快 <br>
> ( 剛剛在上面有提到 ) <br>

<br>

所以 workers 可以看成 **一堆獨立的 process** <br>
而這些 process 會從 message queue 中取得 job 資訊來跑 **CPU bound** 的工作 <br>



<br>

## Redis as Message Queue

我們可以透過 **Redis** 作簡易的 message queue <br>
在 Redis 5.0 之後，Redis 有提供 **Stream** 的資料結構 <br>

<br>

> Redis 原本就有提供 **Pub/Sub** 的功能 <br>
> 但是因為 Pub/Sub 沒有提供資料持久化 <br>
> 當 Redis 當機，就會所有 message 都會丟失 <br>

<br>

而 Stream 解決 Redis Pub/Sub 的問題 <br>
提供**資料持久化**的功能 <br>
並提供 : <br>
- ACK (acknowledgement) : 確認 message 已經被處理
- Consumer Group : 可以讓多個 consumer 來處理同一個 stream

## rq : Redis Queue

我們這邊使用 **`rq`** 來實作 message queue <br>
而 **`rq`** 是一個 **輕量級** 的 **Python job queue** <br>

<br>

`rq` 提供了 **worker** 和 **job queue** 的封裝 <br>
只需要將 job 丟到 job queue 中 <br>
等待 worker 來處理 <br>

<br>

### Queue

我們可以透過 `rq` 的 `Queue` 來建立一個 job queue <br>
```python
from redis import Redis

from rq import Queue

redis_connection = Redis.from_url(settings.redis_url)
task_queue = Queue('rq',connection=redis_connection)
```
### Job

可以使用 `Queue.enqueue` 來將 job 丟到 job queue 中 <br>
> 這邊的 **job** 是指一個要給 worker 的 function <br>
並可以額外設定:
- 執行成功後的 callback function
- timeout ( 超過時間視為失敗 )

```python
job:Job = task_queue.enqueue(
    get_text_from_video,
    video_path,
    hash_name,
    on_success=Callback(report_success),
    ttl=180 # 3 minutes
)
```

而 `enqueue` 會回傳一個 `Job` 物件 <br>
可以再使用 `Job.get_id()` 來取得 job 的 id <br>
回傳給前端，讓前端可以透過這個 id 來查詢 job 的狀態 <br>

<br>

### Worker

> [rq : worker](https://python-rq.org/docs/workers/) <br>

<br>

我們可以直接在 command line 中執行 `rq worker QUEUE_NAME` <br>
來啟動一個 worker 從 `QUEUE_NAME` 中取得 job 來處理 <br>
![rq worker rq](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/rq-worker-rq.png)
<br>

但是在 MacOS 中，會有一個 `fork()` 的問題 <br>
![macos fork() issue](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/macos-fork-issue.png)
> 在這邊查到解決辦法 ：[rq macos issue about `fork()`](https://hynek.me/til/rq-macos/) <br>
需要用:
```bash
export NO_PROXY=*
export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
```

<br>

如果要指定 job 在什麼時候執行 <br>
可以使用 `enqueue_at` 或 `enqueue_in` <br>
並且 `worker` 需要加上 `--with-scheduler` 來啟動 scheduler <br>
> `enqueue_at` : 指定 job 在什麼時間執行，用 `datetime` 來設定 <br>
> `enqueue_in` : 指定 job 在多久後執行，用 `timedelta` 來設定 <br>
> [rq : scheduling](https://python-rq.org/docs/scheduling/) <br>

### 管理 Workers

所以這邊我們寫了 `manage_worker.py` 來 **管理 worker** <br>
因為在 MacOS 中，環境需要設定 `NO_PROXY` 和 `OBJC_DISABLE_INITIALIZE_FORK_SAFETY` <br>
所以這邊我們使用 `subprocess` 並在 `env` 中設定這兩個環境變數 <br>

```python
# ...
subprocess.Popen(
    ["rq","worker",queue_name,"--name",f"worker-{uuid4().hex[:4]}","--with-scheduler"],
    env={
        **os.environ,
        "OBJC_DISABLE_INITIALIZE_FORK_SAFETY":"YES",
        "NO_PROXY":"*"
    }
)
# ...
```

- 可以啟動 n 個 worker
![start 3 workers](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/start-3-workers.png)
- 可以停止所有 worker
![stop all workers](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/stop-all-workers.png)

<br>

## 以 `rq` 實作 非同步 API

### Task API
原本存 `*.mp4` 檔案同樣是由後端 API 處理 <br>
> 畢竟 write file 是 I/O bound 的工作 <br>
> 所以可以由後端 API 處理 <br>


我們可以將原本的 `/api/stt.py` 改成 <br>
```python
@router.post("/task")
async def create_message_queue_task(file: UploadFile = File(...)):
    # save file
    # ...

    # create STT job
    try:
        job = task_queue.enqueue(
            get_text_from_video,
            hash_name,
            on_success=Callback(report_success),
            on_failure=Callback(report_failed),
            ttl=30, # 30 sec timeout
            failure_ttl=60, # 1 minute cleanup for failed job
            result_ttl=180, # result will be kept for 3 minutes
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )
    # ...
```
可以看到我們將 `get_text_from_video` 丟到 job queue 中 <br>
並設定 Callback function 和 timeout 參數 : <br>
- `ttl` : 這個 job 執行多久後會被判斷為 timeout
- `failure_ttl` : 這個 job 執行失敗後，多久後會被刪除
- `result_ttl` : 這個 job 執行成功後，多久後會被刪除
> 這邊的 **刪除** 是指從 Redis 中刪除 <br>

<br>

並加上清除 `*.mp4` 和 `*.wav` 檔案的 job <br>
但是這個 job 要等 STT job 執行完畢後才能執行 <br>
所以這邊使用 `enqueue_in` 來設定 <br>
```python
@router.post("/task")
async def create_message_queue_task(file: UploadFile = File(...)):
    # create STT job
    # ...

    # clean up file job
    try:
        clean_job = task_queue.enqueue_in(
            timedelta(seconds=60),
            clean_file,
            hash_name,
            ttl=10, # 5 minutes timeout
            failure_ttl=20, # 5 minutes cleanup
            result_ttl=20, # 5 minutes cleanup
        )
        print("clean job", clean_job.get_id())
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )
    
    return {
        "job_id": job.get_id(),
        "file_id": hash_name,
    }
```
並在最後回傳 job id 和 file id 給前端 <br>

### Result API

我們的 task API 回傳了 job id 給前端 <br>
所以前端可以透過 job id 來查詢當前 job 的狀態 <br>
使用 `Job.fetch` 來取得 job <br>
`/api/stt.py` <br>
```python
@router.get("/task/{job_id}")
async def get_message_queue_result(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )

    if job.is_finished:
        return {"job_id": job_id, "text": job.result}
    
    return {
        "job_id": job_id,
        "status":"processing"
    }
```
並使用 `Job.is_finished` 來判斷 job 是否執行完畢 <br>
如果執行完畢，就回傳 job id 和結果 <br>

### Benchmark

在 **3 個 workers** 的環境同時送出 **10 個 request** <br>
![3 workers 10 requests](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/3-workers-10-requests.png)
可以看到最慢的 job 從進入 job queue 到執行完畢花了 **25.4** 秒 <br>
比 Naive Solution 的 **48.4** 快了 **一倍** <br>

<br>


在 **10 個 workers** 的環境同時送出 **10 個 request** <br>
![10 workers 10 requests](https://raw.githubusercontent.com/jason810496/iThome2023-FastAPI-Tutorial/Images/assets/Day31/10-workers-10-requests.png)
可以看到最慢的 job 從進入 job queue 到執行完畢花了 **14** 秒 <br>
比 Naive Solution 的 **48.4** 快了 **三倍** <br>

<br>

## 總結

今天我們使用 `rq` 來實作 message queue <br>
並將原本的 API 改成非同步的 API <br>
可以看到在 **10 個 workers** 的環境下 <br>
比 Naive Solution 快了 **三倍** <br>

<br>

所以對於 **需要大量 CPU 資源** 的工作 <br>
或是 **需要花費大量時間** 的工作 <br>
可以考慮使用 message queue 來處理 !<br>




## Reference
- [python run command line code](https://stackabuse.com/executing-shell-commands-with-python/)
- [Python: Convert Speech to text and text to Speech](https://www.geeksforgeeks.org/python-convert-speech-to-text-and-text-to-speech/)
- [rq : performance note](https://python-rq.org/docs/workers/#performance-notes)
- [rq macos issue aboot `fork()`](https://hynek.me/til/rq-macos/)
- [How To Use Server-Sent Events in Node.js to Build a Realtime App](https://www.digitalocean.com/community/tutorials/nodejs-server-sent-events-build-realtime-app)
- [REST API with an asynchronous task queue cluster](https://cloud.tencent.com/developer/article/1943402)
- [install yolo inside docker container](https://lindevs.com/install-yolov8-inside-docker-container-in-linux)
- [Python RabbitMQ 異常重啟機制 Pika重連機制](https://www.jianshu.com/p/60cdc45207cd) 
- [rq : performance note](https://python-rq.org/docs/workers/#performance-notes)