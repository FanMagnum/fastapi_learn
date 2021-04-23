import secrets
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, EmailStr, HttpUrl, PostgresDsn, validator


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    # SECRET_KEY: str = secrets.token_urlsafe(32)
    # # 60 minutes * 24 hours * 8 days = 8 days
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    # SERVER_NAME: str
    # SERVER_HOST: AnyHttpUrl
    # # BACKEND_CORS_ORIGINS is a JSON-formatted list of origins
    # # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    # BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []
    MONGO_HOST: str = "10.176.48.190"
    CELERY_RESULT_BACKEND: Any
    CELERY_NAME: str = 'worker'
    BROKER_URL: Any = 'redis://:letMEin26379+1111@10.176.48.180:27490/9'

    class Config:
        case_sensitive = True


settings = Settings()
