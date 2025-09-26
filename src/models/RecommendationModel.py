from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from typing import List, Optional
from src.models.db_schemas.Recommendation import Recommendation
from src.models.enums import DBEnums
from src.models.BaseModel import BaseModel


class RecommendationModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_RECOMENDATION_NAME.value]

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_RECOMENDATION_NAME.value not in all_collections:
            self.collection = self.db[DBEnums.COLLECTION_RECOMENDATION_NAME.value]
            indexes = Recommendation.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )


     # ---------------- CRUD ---------------- #

    async def create_recommendation(self, recommendation: Recommendation) -> str:
        """Insert a new recommendation document."""
        rec_dict = recommendation.dict(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(rec_dict)
        return str(result.inserted_id)

    async def get_by_user_id(self, rec_id: str) -> Optional[Recommendation]:
        """Fetch a single recommendation by ID."""
        doc = await self.collection.find_one({"_id": ObjectId(rec_id)})
        return Recommendation(**doc) if doc else None

    async def get_user_recommendations(self, user_id: str) -> List[Recommendation]:
        """Fetch all recommendations for a specific user."""
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("createdAt", DESCENDING)
        return [Recommendation(**doc) async for doc in cursor]

    async def update_recommendation_by_rec_id(self, rec_id: str, update_data: dict) -> int:
        """Update recommendation fields by ID."""
        update = {"$set": update_data}
        result = await self.collection.update_one({"_id": ObjectId(rec_id)}, update)
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_recommendation_by_rec_id(self, rec_id: str) -> int:
        """Delete a recommendation by ID."""
        result = await self.collection.delete_one({"_id": ObjectId(rec_id)})
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}
    
    async def delete_recommendations_by_user_id(self, user_id: str):
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}


