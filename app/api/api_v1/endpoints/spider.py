import random
import uuid
import motor.motor_asyncio
import pymongo
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.encoders import jsonable_encoder

from app.bgtesks.generate_report import data2file
from app.bgtesks.nvd_spider import spider
from app.core.config import settings
from app.schemas.apps import Data, SpiderResponse

router = APIRouter()


async def store_task_id(task_id):
    # client = pymongo.MongoClient(host=settings.MONGO_HOST)
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.MONGO_HOST)
    try:
        db = client.cves
        collection = db.taskId
        await collection.insert_one({"task_id": task_id})
    finally:
        client.close()


async def find_task_id(task_id):
    # client = pymongo.MongoClient(host=settings.MONGO_HOST)
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.MONGO_HOST)
    try:
        db = client.cves
        collection = db.taskId
        query = {"task_id": task_id}
        res = await collection.find_one(query)
        if res:
            # find and del
            id = res["_id"]
            await collection.remove(id)
            return True
        return False
    finally:
        client.close()


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
        data: Data,
        background_task: BackgroundTasks
):
    """
    Start spider for apps with below information:
    - **update**: update app info in db, or not
    - **apps**: app info in a list
        - **product**: app name
        - **version**: app version
        - **vendor**: app vendor
    """
    background_task.add_task(spider, jsonable_encoder(data))
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
