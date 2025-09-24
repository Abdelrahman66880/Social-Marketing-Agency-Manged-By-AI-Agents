# The base Model for all database models
from ..helpers.config import get_Settings, Settings

class BaseModel:

    def __init__(self, db_client: object):
        self.db_client = db_client
        self.app_settings = get_Settings()