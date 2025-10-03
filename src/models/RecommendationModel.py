from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from typing import List, Optional, Dict, Any
from src.models.db_schemas.Recommendation import Recommendation
from src.models.enums import DBEnums
from src.models.BaseModel import BaseModel


class RecommendationModel(BaseModel):
    def __init__(self, db_client: AsyncIOMotorClient):
        """
        Model class for handling CRUD operations on the Recommendation collection.

        Args:
            db_client (AsyncIOMotorClient): Async MongoDB client instance.
        """
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_RECOMENDATION_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient) -> "RecommendationModel":
        """
        Create and initialize a RecommendationModel instance.

        Args:
            db_client (AsyncIOMotorClient): Async MongoDB client instance.

        Returns:
            RecommendationModel: Initialized instance of RecommendationModel.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """
        Initialize the recommendations collection if it does not exist.
        Creates indexes defined in the Recommendation schema.

        Returns:
            None
        """
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

    async def create_recommendation(self, recommendation: Recommendation) -> Recommendation:
        """
        Insert a new recommendation document.

        Args:
            recommendation (Recommendation): Recommendation object to insert.

        Returns:
            str: The inserted document's ID as a string.
        """
        rec_dict = recommendation.dict(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(rec_dict)
        return recommendation

    async def get_by_user_id(self, rec_id: str) -> Optional[Recommendation]:
        """
        Fetch a single recommendation by its ID.

        Args:
            rec_id (str): Recommendation document ID.

        Returns:
            Optional[Recommendation]: Recommendation object if found, otherwise None.
        """
        doc = await self.collection.find_one({"_id": ObjectId(rec_id)})
        return Recommendation(**doc) if doc else None

    async def get_user_recommendations(self, user_id: str) -> List[Recommendation]:
        """
        Fetch all recommendations for a specific user, sorted by creation date (newest first).

        Args:
            user_id (str): User's ObjectId as a string.

        Returns:
            List[Recommendation]: List of Recommendation objects.
        """
        cursor = self.collection.find({"user_id": ObjectId(user_id)}).sort("createdAt", DESCENDING)
        return [Recommendation(**doc) async for doc in cursor]

    async def update_recommendation_by_rec_id(self, rec_id: str, update_data: Dict[str, Any]) -> Dict[str, int]:
        """
        Update recommendation fields by recommendation ID.

        Args:
            rec_id (str): Recommendation document ID.
            update_data (dict): Fields to update.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        update = {"$set": update_data}
        result = await self.collection.update_one({"_id": ObjectId(rec_id)}, update)
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_recommendation_by_rec_id(self, rec_id: str) -> Dict[str, int]:
        """
        Delete a recommendation by ID.

        Args:
            rec_id (str): Recommendation document ID.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        result = await self.collection.delete_one({"_id": ObjectId(rec_id)})
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_recommendations_by_user_id(self, user_id: str) -> Dict[str, int]:
        """
        Delete all recommendations for a specific user.

        Args:
            user_id (str): User's ObjectId as a string.

        Returns:
            dict: {"deleted_count": int}
        """
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}