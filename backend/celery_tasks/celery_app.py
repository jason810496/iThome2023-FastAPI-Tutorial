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
