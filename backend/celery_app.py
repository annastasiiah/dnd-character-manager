import os

from celery import Celery

celery_app = Celery(
    "dnd_manager",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1"),
    include=["tasks.character_export"], 
)