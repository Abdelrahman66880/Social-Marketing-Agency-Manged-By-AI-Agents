from typing import List, Optional, Dict, Any
from bson import ObjectId
from uuid import uuid4
from datetime import time
from src.models.BaseModel import BaseModel
from src.models.db_schemas.Schedule import Schedule, ScheduledPost, ScheduledCompetitorAnalysis, InteractionAnalysisDate
from src.models.enums.DBEnums import DBEnums


class ScheduleModel(BaseModel):
    def __init__(self, db_client):
        """
        ScheduleModel handles CRUD operations and nested schedule management for a user's schedule.

        Args:
            db_client: The async MongoDB client instance.
        """
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_SCHEDULE_NAME.value]

    @classmethod
    async def create_instance(cls, db_client) -> "ScheduleModel":
        """
        Create an instance of ScheduleModel and initialize its collection.

        Args:
            db_client: The async MongoDB client instance.

        Returns:
            ScheduleModel: Initialized instance of ScheduleModel.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """
        Initialize the MongoDB collection if it does not exist.
        Creates indexes defined in the Schedule schema.

        Returns:
            None
        """
        all_collections = await self.db.list_collection_names()
        if DBEnums.COLLECTION_SCHEDULE_NAME.value not in all_collections:
            self.collection = self.db[DBEnums.COLLECTION_SCHEDULE_NAME.value]
            indexes = Schedule.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index.get("unique", False)
                )

    # ---------------- CRUD ---------------- #

    async def create_schedule(self, schedule: Schedule) -> ObjectId:
        """
        Create a new schedule for a user. Generates UUIDs for nested items.

        Args:
            schedule (Schedule): Schedule object to be inserted.

        Returns:
            Schedule ID: The created schedule ID.
        """
        for post in schedule.posts:
            post.id = str(uuid4())
        for analysis in schedule.competitor_analysis:
            analysis.id = str(uuid4())
        for date in schedule.interaction_analysis_dates:
            date.id = str(uuid4())

        result = await self.collection.insert_one(schedule.model_dump(by_alias=True, exclude_unset=True))
        return result.inserted_id

    async def get_by_user_id(self, user_id: str) -> Optional[Schedule]:
        """
        Retrieve a schedule by user ID.

        Args:
            user_id (str): The user's ObjectId as a string.

        Returns:
            Optional[Schedule]: Schedule object if found, else None.
        """
        result = await self.collection.find_one({"user_id": user_id})
        return Schedule(**result) if result else None

    async def replace_schedule_by_user_id(self, user_id: str, new_schedule: Schedule) -> Dict[str, int]:
        """
        Replace the entire schedule for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            new_schedule (Schedule): The full new schedule to replace the old one.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        # Generate IDs for new nested elements if not provided
        for post in new_schedule.posts:
            post.id = post.id or str(uuid4())
        for analysis in new_schedule.competitor_analysis:
            analysis.id = analysis.id or str(uuid4())
        for date in new_schedule.interaction_analysis_dates:
            date.id = date.id or str(uuid4())

        # Validate that no duplicates exist in the new schedule (reuses your validator)
        new_schedule = Schedule(**new_schedule.model_dump())

        existing = await self.collection.find_one({"user_id": user_id}, {"_id": 1})
        if not existing:
            return {"matched_count": 0, "modified_count": 0, "_id": None}

        # Assign the same _id so MongoDB doesn't complain
        new_doc = new_schedule.model_dump(by_alias=True, exclude_unset=True)
        new_doc["_id"] = existing["_id"]

        result = await self.collection.replace_one(
            {"user_id": user_id},
            new_doc
        )

        return {"matched_count": result.matched_count, "modified_count": result.modified_count, "_id": new_doc["_id"]}

    async def delete_by_id(self, schedule_id: str) -> Dict[str, int]:
        """
        Delete a schedule by user ID.

        Args:
            schedule_id (str): The Schedule's ObjectId as a string.

        Returns:
            dict: {"deleted_count": int}
        """
        result = await self.collection.delete_one({"_id": ObjectId(schedule_id)})
        return {"deleted_count": result.deleted_count}


    async def exists_for_user(self, user_id: str) -> bool:
        """
        Check if a schedule exists for a given user.

        Args:
            user_id (str): The user's ObjectId as a string.

        Returns:
            bool: True if schedule exists, else False.
        """
        result = await self.collection.find_one({"user_id": user_id}, {"_id": 1})
        return result is not None
