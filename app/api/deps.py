import hashlib
from datetime import datetime

from fastapi import Header, HTTPException


def get_current_api_key():
    today = datetime.utcnow().date()
    string = str(today) + "supersecret"
    api_key = hashlib.md5(string.encode('utf-8')).hexdigest()
    return api_key


async def verify_api_key(api_key: str = Header(...)):
    if api_key != get_current_api_key():
        raise HTTPException(status_code=400, detail="api-key header invalid")