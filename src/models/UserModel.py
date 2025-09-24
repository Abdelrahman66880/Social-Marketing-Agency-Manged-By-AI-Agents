# Customer Model-
from .BaseModel import BaseModel
from .db_schemas import User
from .enums.UserEnums import AccountStatus
from .enums.DBEnums import DBEnums
from bson.objectid import ObjectId

class UserModel(BaseModel):

    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_USER_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_USER_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnums.COLLECTION_USER_NAME.value]
            indexes = User.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index['key'],
                    name= index['name'],
                    unique=index['unique'],
                    sparse= index['sparse']
                )
