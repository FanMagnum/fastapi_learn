import uvicorn
from fastapi import FastAPI

from app.api.api_v1 import api
from app.core.config import settings

app = FastAPI(
    title="Spider 4 app cve"
)

app.include_router(api.api_router, prefix=settings.API_V1_STR)

if __name__ == '__main__':
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True, workers=4)
