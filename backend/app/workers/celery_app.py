from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "cloud_security_scanner",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.workers.tasks"],
)

celery_app.conf.update(task_track_started=True, task_time_limit=900)
