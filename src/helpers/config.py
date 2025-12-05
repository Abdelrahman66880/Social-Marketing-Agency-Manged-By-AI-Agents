import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # points to src/

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    MONGODB_URL: str
    MONGODB_DATABASE: str
    GRAPH_API_VERSION: str
    PAGE_ACCESS_TOKEN: str
    PAGE_ID: str
    WEB_HOOK_VERIFY_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int
    BETTERSTACK_SOURCE_TOKEN: str

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")  # src/.env

def get_Settings():
    return Settings()

