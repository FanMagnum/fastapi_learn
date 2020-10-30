import json
from os import path
from pprint import pprint

import motor.motor_asyncio
from pymongo import MongoClient

from app.core.config import settings


async def data2file():
    # client = MongoClient(host=settings.MONGO_HOST)
    client = motor.motor_asyncio.AsyncIOMotorClient(host=settings.MONGO_HOST)
    current_path = path.dirname(__file__)
    try:
        db = client.cves
        collection = db.spider

        apps = await collection.find()
        data = []
        for app in apps:
            tmp = app
            tmp.pop('_id')
            if app['cves']:
                tmp["cve_count"] = len(app['cves'])
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
    finally:
        client.close()


if __name__ == '__main__':
    import time

    start = time.time()
    data2file()
    print(f"Running time: {time.time() - start}")
