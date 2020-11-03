import uuid
import motor.motor_asyncio
from odmantic import AIOEngine
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder

from app.bgtasks.generate_report import data2file
from app.core.celery_app import celery_app
from app.core.config import settings
from app.models.task_id import TaskId
from app.schemas.apps import Data, SpiderResponse

router = APIRouter()


async def store_task_id(task_id):
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.MONGO_HOST)
    engine = AIOEngine(motor_client=client, database='cves')
    task = TaskId(task_id=task_id)
    await engine.save(task)


async def find_task_id(task_id):
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.MONGO_HOST)
    engine = AIOEngine(motor_client=client, database='cves')
    task = await engine.find_one(TaskId, TaskId.task_id == task_id)
    if task:
        await engine.delete(task)
        return True
    return False


@router.post(
    '/',
    response_model=SpiderResponse,
    # response_model_exclude_unset=True,
    # tags=['spider'],
    summary='start spider',
    response_description='Response spider task id'
)
async def start_spider(
        *,
        data: Data
):
    """
    Start spider for apps with below information:
    - **update**: update app info in db, or not
    - **apps**: app info in a list
        - **product**: app name
        - **version**: app version
        - **vendor**: app vendor
    """
    task = celery_app.send_task("app.bgtasks.nvd_spider.spider",
                                args=[jsonable_encoder(data)])
    uid = str(uuid.uuid4())
    task_id = ''.join(uid.split('-'))
    await store_task_id(task_id)
    res = {"message": "success", 'task_id': task_id}
    return res


@router.get("/report")
async def generate_report(task_id: str, background_task: BackgroundTasks):
    if not await find_task_id(task_id):
        raise HTTPException(status_code=400, detail="Invalid task id")
    background_task.add_task(data2file)
    res = {"message": "generate report success", "url": ""}
    return res
