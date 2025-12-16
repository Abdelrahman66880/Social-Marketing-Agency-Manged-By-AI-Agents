# The base Model for all database models
from src.helpers.config import get_Settings, Settings

class BaseModel:

    def __init__(self, db_client: object):
        self.app_settings = get_Settings()
        
        # Determine if db_client is a Database or Client
        # Use isinstance because MotorClient dynamic attributes make hasattr return True for everything
        from motor.motor_asyncio import AsyncIOMotorDatabase
        
        if isinstance(db_client, AsyncIOMotorDatabase): # It is a Database
             self.db = db_client
             self.db_client = db_client.client
        else: # It is a Client (or assumed to be)
             self.db_client = db_client
             self.db = self.db_client[self.app_settings.MONGODB_DATABASE]