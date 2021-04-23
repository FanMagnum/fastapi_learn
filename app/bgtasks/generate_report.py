import json
from os import path

from pymongo import MongoClient

from app.core.config import settings
from app.core.log import logger


def data2file():
    client = MongoClient(host=settings.MONGO_HOST)
    current_path = path.dirname(__file__)
    try:
        db = client.cves
        collection = db.app_spider
        apps = collection.find()
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
                logger.success("report file update successful...")
    finally:
        client.close()


