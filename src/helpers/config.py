import os
from pydantic_settings import BaseSettings

BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # points to src/

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str
    MONGODB_URL: str
    API_BASE_URL: str
    MONGODB_DATABASE: str
    GRAPH_API_VERSION: str
    FACEBOOK_APP_ID: str
    FACEBOOK_APP_SECRET: str
    ENCRYPTION_KEY: str
    WEB_HOOK_VERIFY_TOKEN: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_DAYS: int

    class Config:
        env_file = os.path.join(BASE_DIR, ".env")  # src/.env

def get_Settings() -> Settings:
    """
    Creates and returns an instance of the Settings class, loading configuration from environment variables.

    Args:
        None

    Returns:
        Settings: An instance of the Settings class containing validated application configuration.

    Raises:
        pydantic.ValidationError: If required environment variables are missing or invalid.
    """
    return Settings()
