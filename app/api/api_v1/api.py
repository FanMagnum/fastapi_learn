from fastapi import APIRouter, Depends

from app.api.api_v1.endpoints import spider
from app.api.deps import verify_api_key

api_router = APIRouter()
api_router.include_router(
    spider.router,
    prefix="/spider",
    tags=["spider"],
    dependencies=[Depends(verify_api_key)]
)
