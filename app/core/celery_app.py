from celery import Celery

from app.core.config import settings

celery_app = Celery("worker", broker=settings.BROKER_URL)

celery_app.conf.task_routes = {"app.bgtasks.nvd_spider.spider": "spider"}