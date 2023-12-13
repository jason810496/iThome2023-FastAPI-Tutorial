from fastapi import APIRouter  , HTTPException
from fastapi import File, UploadFile
import aiofiles
from uuid import uuid4

from setting.config import get_settings
from jobs.stt import get_text_from_video , report_success , report_failed , clean_file
from redis import Redis

from rq import Queue , Callback
from rq.job import Job
from datetime import timedelta


settings = get_settings()

router = APIRouter(
    tags=["speech to text"],
    prefix="/stt",
)

redis_conn = Redis.from_url(settings.redis_url)
task_queue = Queue('rq',connection=redis_conn, default_timeout=60) # timeout 60 seconds

@router.post("/native")
async def native_processing(file: UploadFile = File(...)):
    save_path = settings.upload_path

    ext_name = file.filename.split(".")[-1]
    hash_name = uuid4().hex[:8]

    out_file_path = f"{save_path}/{hash_name}.{ext_name}"
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    text = get_text_from_video(uuid=hash_name)

    return {"job_id": hash_name, "text": text}


@router.post("/task")
async def create_message_queue_task(file: UploadFile = File(...)):
    save_path = settings.upload_path
    ext_name = file.filename.split(".")[-1]
    hash_name = uuid4().hex[:8]

    out_file_path = f"{save_path}/{hash_name}.{ext_name}"
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    try:

        job = task_queue.enqueue(
            get_text_from_video,
            hash_name,
            on_success=Callback(report_success),
            on_failure=Callback(report_failed),
            ttl=30, # 3 minutes timeout
            failure_ttl=60, # 5 minutes cleanup
            result_ttl=180, # 5 minutes cleanup
        )
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )
    

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

@router.get("/task/{job_id}")
async def get_message_queue_result(job_id: str):
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )


    print(job.is_finished)
    print(job.__dict__)

    if job.is_finished:
        return {"job_id": job_id, "text": job.result}
    
    return {
        "job_id": job_id,
        "status":"processing"
    }