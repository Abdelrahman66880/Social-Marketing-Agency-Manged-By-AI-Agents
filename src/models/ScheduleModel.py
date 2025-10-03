from typing import List, Optional, Dict, Any
from bson import ObjectId
from uuid import uuid4
from datetime import time
from src.models.BaseModel import BaseModel
from src.models.db_schemas.Schedule import Schedule, ScheduledPost, ScheduledCompetitorAnalysis, interactionAnalysisDate
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
        all_collections = await self.db_client.list_collection_names()
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

    async def create_schedule(self, schedule: Schedule) -> Schedule:
        """
        Create a new schedule for a user. Generates UUIDs for nested items.

        Args:
            schedule (Schedule): Schedule object to be inserted.

        Returns:
            Schedule: The created schedule with assigned IDs and inserted MongoDB ID.
        """
        for post in schedule.posts:
            post.id = str(uuid4())
        for analysis in schedule.competitor_analysis:
            analysis.id = str(uuid4())
        for date in schedule.interaction_analysis_dates:
            date.id = str(uuid4())

        result = await self.collection.insert_one(schedule.dict(by_alias=True, exclude_unset=True))
        schedule.id = result.inserted_id
        return schedule

    async def get_by_user_id(self, user_id: str) -> Optional[Schedule]:
        """
        Retrieve a schedule by user ID.

        Args:
            user_id (str): The user's ObjectId as a string.

        Returns:
            Optional[Schedule]: Schedule object if found, else None.
        """
        result = await self.collection.find_one({"user_id": ObjectId(user_id)})
        return Schedule(**result) if result else None

    async def update_schedule_by_user_id(self, user_id: str, update_data: dict) -> Dict[str, int]:
        """
        Update a schedule by user ID.

        Args:
            user_id (str): The user's ObjectId as a string.
            update_data (dict): Dictionary of fields to update.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_by_user_id(self, user_id: str) -> Dict[str, int]:
        """
        Delete a schedule by user ID.

        Args:
            user_id (str): The user's ObjectId as a string.

        Returns:
            dict: {"deleted_count": int}
        """
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}

    async def list_schedules(self, page_no: int = 1, page_size: int = 20) -> List[Schedule]:
        """
        List schedules with pagination.

        Args:
            page_no (int, optional): Page number (default: 1).
            page_size (int, optional): Number of items per page (default: 20).

        Returns:
            List[Schedule]: List of Schedule objects.
        """
        cursor = self.collection.find().skip((page_no - 1) * page_size).limit(page_size)
        results = await cursor.to_list(length=page_size)
        return [Schedule(**doc) for doc in results]

    async def exists_for_user(self, user_id: str) -> bool:
        """
        Check if a schedule exists for a given user.

        Args:
            user_id (str): The user's ObjectId as a string.

        Returns:
            bool: True if schedule exists, else False.
        """
        result = await self.collection.find_one({"user_id": ObjectId(user_id)}, {"_id": 1})
        return result is not None

    # ---------------- Add nested items ---------------- #

    async def _check_conflict(self, user_id: str, collection_name: str, new_day: str, new_time: time, exclude_id: Optional[str] = None) -> None:
        """
        Check if a new item conflicts with an existing one (same day and time).

        Args:
            user_id (str): The user's ObjectId as a string.
            collection_name (str): Name of the nested collection ("posts", "competitor_analysis", etc.).
            new_day (str): Day of the week.
            new_time (time): Time of the day.
            exclude_id (str, optional): ID to exclude from conflict check.

        Raises:
            ValueError: If a conflict is detected.

        Returns:
            None
        """
        query = {
            "user_id": ObjectId(user_id),
            f"{collection_name}": {
                "$elemMatch": {
                    "day_of_week": new_day,
                    "time_of_day": new_time,
                }
            }
        }
        if exclude_id:
            query[f"{collection_name}.id"] = {"$ne": exclude_id}

        conflict = await self.collection.find_one(query)
        if conflict:
            raise ValueError(f"Conflict: another {collection_name[:-1]} is already scheduled at {new_day} {new_time}")

    async def add_post_by_user_id(self, user_id: str, post: ScheduledPost) -> Dict[str, int]:
        """
        Add a new scheduled post for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            post (ScheduledPost): Scheduled post object.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        post.id = str(uuid4())
        await self._check_conflict(user_id, "posts", post.day_of_week, post.time_of_day)
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"posts": post.dict(exclude_unset=True)}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def add_competitor_analysis_by_user_id(self, user_id: str, analysis: ScheduledCompetitorAnalysis) -> Dict[str, int]:
        """
        Add a new scheduled competitor analysis for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            analysis (ScheduledCompetitorAnalysis): Competitor analysis object.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        analysis.id = str(uuid4())
        await self._check_conflict(user_id, "competitor_analysis", analysis.day_of_week, analysis.time_of_day)
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"competitor_analysis": analysis.dict(exclude_unset=True)}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def add_interaction_date_by_user_id(self, user_id: str, date: interactionAnalysisDate) -> Dict[str, int]:
        """
        Add a new scheduled interaction analysis date for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            date (interactionAnalysisDate): Interaction analysis date object.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        date.id = str(uuid4())
        await self._check_conflict(user_id, "interaction_analysis_dates", date.day_of_week, date.time_of_day)
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"interaction_analysis_dates": date.dict(exclude_unset=True)}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    # ---------------- Update nested items ---------------- #

    async def update_post(self, user_id: str, post_id: str, update_data: dict) -> Dict[str, int]:
        """
        Update a scheduled post for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            post_id (str): ID of the post to update.
            update_data (dict): Fields to update.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        new_day = update_data.get("day_of_week")
        new_time = update_data.get("time_of_day")
        if new_day and new_time:
            await self._check_conflict(user_id, "posts", new_day, new_time, exclude_id=post_id)

        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id), "posts.id": post_id},
            {"$set": {f"posts.$.{k}": v for k, v in update_data.items()}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_competitor_analysis(self, user_id: str, analysis_id: str, update_data: dict) -> Dict[str, int]:
        """
        Update a scheduled competitor analysis for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            analysis_id (str): ID of the competitor analysis to update.
            update_data (dict): Fields to update.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        new_day = update_data.get("day_of_week")
        new_time = update_data.get("time_of_day")
        if new_day and new_time:
            await self._check_conflict(user_id, "competitor_analysis", new_day, new_time, exclude_id=analysis_id)

        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id), "competitor_analysis.id": analysis_id},
            {"$set": {f"competitor_analysis.$.{k}": v for k, v in update_data.items()}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_interaction_date(self, user_id: str, date_id: str, update_data: dict) -> Dict[str, int]:
        """
        Update a scheduled interaction analysis date for a user.

        Args:
            user_id (str): The user's ObjectId as a string.
            date_id (str): ID of the interaction analysis date to update.
            update_data (dict): Fields to update.

        Returns:
            dict: {"matched_count": int, "modified_count": int}
        """
        new_day = update_data.get("day_of_week")
        new_time = update_data.get("time_of_day")
        if new_day and new_time:
            await self._check_conflict(user_id, "interaction_analysis_dates", new_day, new_time, exclude_id=date_id)

        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id), "interaction_analysis_dates.id": date_id},
            {"$set": {f"interaction_analysis_dates.$.{k}": v for k, v in update_data.items()}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}
