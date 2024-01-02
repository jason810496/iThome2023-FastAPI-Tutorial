from __future__ import absolute_import, unicode_literals
from .celery_app import app
from celery import subtask


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)


@app.task
def clean_up(job_id: str,file_name: str):
    import os

    os.remove(f"tmp_content/{job_id}/{file_name}")
    os.rmdir(f"tmp_content/{job_id}")
    os.remove(f"upload_content/{file_name}")


@app.task(bind=True)
def yolo_predict(self, file_name: str):
    from ultralytics import YOLO

    # run this command using YOLO
    # yolo predict model=yolov8n-seg.pt source='data/dog.jpg' project=save_images name=xxxxx save


    job_id = self.request.id

    YOLO("yolov8n.pt").predict(
        source=f"upload_content/{file_name}",
        project="tmp_content",
        name=job_id,
        save=True,
    )

    # clean up after 1 minute
    subtask("celery_tasks.tasks.clean_up").apply_async(kwargs={"job_id": job_id, "file_name": file_name}, countdown=60)

    return {"success": True, "file": file_name}


@app.task
def test(name: str):
    import time

    time.sleep(5)
    try:
        return {"success": True, "name": name}
    except Exception as e:
        return {"error": str(e)}


def yolo_predict_native(file_name: str):
    from ultralytics import YOLO

    # run this command using YOLO
    # yolo predict model=yolov8n-seg.pt source='data/dog.jpg' project=save_images name=xxxxx save

    try:
        YOLO("yolov8n.pt").predict(
            source=f"upload_content/{file_name}",
            project="tmp_content",
            name=".",
            save=True,
        )
        return {"status": "success"}
    except Exception as e:
        return {"status": "failed", "error": str(e)}
