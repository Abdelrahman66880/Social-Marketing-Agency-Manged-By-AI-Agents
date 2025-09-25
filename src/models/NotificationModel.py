from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from typing import List, Optional
from db_schemas.Notification import Notification
import BaseModel
from .enums import DBEnums


class NotificationModel(BaseModel):
    def __init__(self, db_client: AsyncIOMotorClient):
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_NOTIFICATION_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_NOTIFICATION_NAME.value not in all_collections:
            self.collection = self.db[DBEnums.COLLECTION_NOTIFICATION_NAME.value]
            indexes = Notification.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )

    # ---------------- CRUD ---------------- #

    async def create_notification(self, notification: Notification) -> str:
        """Insert a new notification document."""
        notif_dict = notification.dict(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(notif_dict)
        return str(result.inserted_id)

    async def get_by_id(self, notif_id: str) -> Optional[Notification]:
        """Fetch a single notification by ID."""
        doc = await self.collection.find_one({"_id": ObjectId(notif_id)})
        return Notification(**doc) if doc else None

    async def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Notification]:
        """Fetch recent notifications for a specific user, newest first."""
        cursor = (
            self.collection.find({"user_id": ObjectId(user_id)})
            .sort("createdAt", DESCENDING)
            .limit(limit)
        )
        return [Notification(**doc) async for doc in cursor]

    async def mark_as_seen(self, notif_id: str) -> dict:
        """Mark a notification as seen."""
        result = await self.collection.update_one(
            {"_id": ObjectId(notif_id)},
            {"$set": {"seen": True}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_notification(self, notif_id: str, update_data: dict) -> dict:
        """Update notification fields by ID."""
        update = {"$set": update_data}
        result = await self.collection.update_one({"_id": ObjectId(notif_id)}, update)
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_notification_by_id(self, notif_id: str) -> dict:
        """Delete a single notification by ID."""
        result = await self.collection.delete_one({"_id": ObjectId(notif_id)})
        return {"deleted_count": result.deleted_count}

    async def delete_notifications_by_user_id(self, user_id: str) -> dict:
        """Delete all notifications for a specific user."""
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}
