from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import DESCENDING
from typing import List, Optional
from src.models.db_schemas.Notification import Notification
from src.models.BaseModel import BaseModel
from src.models.enums.DBEnums import DBEnums


class NotificationModel(BaseModel):
    """
    Data access layer for handling Notification documents in MongoDB.

    This class provides CRUD operations for notifications stored in the
    `COLLECTION_NOTIFICATION_NAME` collection, as defined in DBEnums.
    It uses Motor (async MongoDB driver) to perform non-blocking database operations.
    """

    def __init__(self, db_client: AsyncIOMotorClient):
        """
        Initialize NotificationModel with the provided database client.

        Args:
            db_client (AsyncIOMotorClient): The MongoDB client.
        """
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_NOTIFICATION_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: AsyncIOMotorClient) -> "NotificationModel":
        """
        Factory method to create and initialize an instance.

        Ensures that the required collection and indexes exist before returning the instance.

        Args:
            db_client (AsyncIOMotorClient): The MongoDB client.

        Returns:
            NotificationModel: An initialized instance.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self)-> None:
        """
        Initialize the collection and ensure necessary indexes are created.
        If the collection does not exist, it is created and indexes are applied.
        """
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

    async def create_notification(self, notification: Notification) -> Notification:
        """
        Insert a new notification document into the database.

        Args:
            notification (Notification): The notification object to insert.

        Returns:
            Notification: The inserted notification object with its generated ID.
        """
        notif_dict = notification.model_dump(by_alias=True, exclude_none=True)
        result = await self.collection.insert_one(notif_dict)
        notification.id = str(result.inserted_id)
        return notification


    async def get_by_id(self, notif_id: str) -> Optional[Notification]:
        """
        Fetch a single notification by its ID.

        Args:
            notif_id (str): The ID of the notification.

        Returns:
            Optional[Notification]: The notification if found, else None.
        """
        doc = await self.collection.find_one({"_id": ObjectId(notif_id)})
        return Notification(**doc) if doc else None

    async def get_user_notifications(self, user_id: str, limit: int = 50) -> List[Notification]:
        """
        Fetch recent notifications for a specific user, sorted by newest first.

        Args:
            user_id (str): The ID of the user.
            limit (int, optional): Maximum number of notifications to fetch. Defaults to 50.

        Returns:
            List[Notification]: A list of user notifications.
        """
        cursor = (
            self.collection.find({"user_id": user_id})
            .sort("createdAt", DESCENDING)
            .limit(limit)
        )
        return [Notification(**doc) async for doc in cursor]

    async def mark_as_seen(self, notif_id: str) -> dict:
        """
        Mark a notification as seen.

        Args:
            notif_id (str): The ID of the notification.

        Returns:
            dict: Update result with matched and modified counts.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(notif_id)},
            {"$set": {"seen": True}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_notification(self, notif_id: str, update_data: dict) -> dict:
        """
        Update notification fields by ID.

        Args:
            notif_id (str): The ID of the notification to update.
            update_data (dict): The fields and values to update.

        Returns:
            dict: Update result with matched and modified counts.
        """
        update = {"$set": update_data}
        result = await self.collection.update_one({"_id": ObjectId(notif_id)}, update)
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_notification_by_id(self, notif_id: str) -> dict:
        """
        Delete a single notification by its ID.

        Args:
            notif_id (str): The ID of the notification.

        Returns:
            dict: Delete result with deleted count.
        """
        result = await self.collection.delete_one({"_id": ObjectId(notif_id)})
        return {"deleted_count": result.deleted_count}

    async def delete_notifications_by_user_id(self, user_id: str) -> dict:
        """
        Delete all notifications belonging to a specific user.

        Args:
            user_id (str): The ID of the user.

        Returns:
            dict: Delete result with deleted count.
        """
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}
