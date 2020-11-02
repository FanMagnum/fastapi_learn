import json
from os import path
from pprint import pprint

import motor.motor_asyncio
from odmantic import AIOEngine
from pymongo import MongoClient

from app.core.config import settings
from app.models.apps import AppSpider


async def data2file():
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.MONGO_HOST)
    engine = AIOEngine(motor_client=client, database='cves')
    current_path = path.dirname(__file__)
    data = []
    async for app in engine.find(AppSpider):
        tmp = dict(app)
        print(tmp)
        tmp.pop('id')
        if app.cves:
            tmp["cve_count"] = len(app.cves)
        else:
            tmp['cve_count'] = 0
        # pprint(tmp)
        data.append(tmp)

    with open(f"{path.dirname(path.dirname(current_path))}/result.json", 'r') as f:
        raw_data = json.load(f)
    if raw_data != data:
        # Data has been changed
        with open(f"{path.dirname(path.dirname(current_path))}/result.json", "w") as f:
            json.dump(data, f)
            print("report file update successful...")


if __name__ == '__main__':
    import time

    start = time.time()
    data2file()
    print(f"Running time: {time.time() - start}")
