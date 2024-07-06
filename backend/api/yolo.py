from fastapi import APIRouter  , HTTPException
from fastapi import File, UploadFile
from fastapi import Response  
from fastapi.responses import StreamingResponse   
import aiofiles
from uuid import uuid4
import aiofiles
from celery_tasks.tasks import yolo_predict_native , yolo_predict , test
from celery.result import AsyncResult

from setting.config import get_settings


settings = get_settings()

router = APIRouter(
    tags=["object detection"],
    prefix="/yolo",
)


@router.post("/native")
async def native_processing(file: UploadFile = File(...)):
    save_path = settings.upload_path

    ext_name = file.filename.split(".")[-1]
    hash_name = uuid4().hex[:8]

    out_file_path = f"{save_path}/{hash_name}.{ext_name}"
    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    result = yolo_predict_native(file_name=f"{hash_name}.{ext_name}")

    return {"job_id": hash_name, **result}


@router.post("/task")
async def create_message_queue_task(file: UploadFile = File(...)):
    # save file
    save_path = settings.upload_path
    ext_name = file.filename.split(".")[-1]
    hash_name = uuid4().hex[:8]
    out_file_path = f"{save_path}/{hash_name}.{ext_name}"

    async with aiofiles.open(out_file_path, 'wb') as out_file:
        content = await file.read()  # async read
        await out_file.write(content)  # async write

    # create celery task
    try:
        job:AsyncResult = yolo_predict.delay(file_name=f"{hash_name}.{ext_name}")
        print(job)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )
    
    # clean up file job
    # try:
        
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=500, detail=str(e)  )
    
    return {
        "job_id": str(job),
        "file_id": hash_name,
    }

@router.get("/task/{job_id}")
async def get_message_queue_result(job_id: str):
    try:
        job = AsyncResult(job_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )


    return{
        "job_id": job_id,
        "status": job.status,
        "result": job.result,
    }

import pydantic
media_response_model = pydantic.create_model(
    "media_response_model",
    content=(bytes, ...),
    media_type=(str, ...),
)

# show image
@router.get("/task/{job_id}/result", response_model=media_response_model)
async def get_message_queue_result(job_id: str):
    try:
        job = AsyncResult(job_id)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e)  )
    
    if job.status != "SUCCESS":
        return {"status": job.status}


    path = f"tmp_content/{job.id}/{job.result['file']}" 
    extension = path.split(".")[-1]
    m_type = "image"
    if extension == "mp4":
        m_type = "video"

    async def iterfile():
        async with aiofiles.open(path, mode="rb") as file_like:
            content = await file_like.read(1024)
            while content:
                yield content
                content = await file_like.read(1024)
    
    return StreamingResponse(iterfile(), media_type=f"{m_type}/{extension}")

    # return Response(content=open(path, "rb").read(), media_type=f"{m_type}/{extension}")