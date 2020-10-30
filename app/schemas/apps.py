from typing import Optional, List

from pydantic import BaseModel


class App(BaseModel):
    product: str
    version: str = ''
    vendor: Optional[str] = None


class Data(BaseModel):
    update: bool = False
    apps: List[App]

    # docs模板
    class Config:
        schema_extra = {
            "example": {
                "update": False,
                "apps": [
                    {
                        "product": "7-Zip 18.05 (x64)",
                        "version": "18.05",
                        "vendor": "Igor Pavlov"
                    }, {
                        "product": "7-Zip 19.00",
                        "version": "19.00",
                        "vendor": "Igor Pavlov"
                    }
                ]
            }
        }


class SpiderResponse(BaseModel):
    message: str
    task_id: str

    class Config:
        schema_extra = {
            "example": {
                "message": "success",
                "task_id": "Abcd234Tre"
            }
        }
