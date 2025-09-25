from typing import List, Optional
from bson import ObjectId
from uuid import uuid4
from datetime import time
from .BaseModel import BaseModel
from .db_schemas import Schedule, ScheduledPost, ScheduledCompetitorAnalysis, Date
from .enums.DBEnums import DBEnums


class ScheduleModel(BaseModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_SCHEDULE_NAME.value]

    @classmethod
    async def create_instance(cls, db_client):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
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
        # Assign UUIDs to nested items
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
        result = await self.collection.find_one({"user_id": ObjectId(user_id)})
        return Schedule(**result) if result else None

    async def update_schedule_by_user_id(self, user_id: str, update_data: dict) -> dict:
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_by_user_id(self, user_id: str) -> dict:
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}

    async def list_schedules(self, page_no: int = 1, page_size: int = 20) -> List[Schedule]:
        cursor = self.collection.find().skip((page_no - 1) * page_size).limit(page_size)
        results = await cursor.to_list(length=page_size)
        return [Schedule(**doc) for doc in results]

    async def exists_for_user(self, user_id: str) -> bool:
        result = await self.collection.find_one({"user_id": ObjectId(user_id)}, {"_id": 1})
        return result is not None

    # ---------------- Add nested items ---------------- #

    async def _check_conflict(self, user_id: str, collection_name: str, new_day, new_time, exclude_id=None):
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

    async def add_post_by_user_id(self, user_id: str, post: ScheduledPost) -> dict:
        post.id = str(uuid4())
        await self._check_conflict(user_id, "posts", post.day_of_week, post.time_of_day)
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"posts": post.dict(exclude_unset=True)}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def add_competitor_analysis_by_user_id(self, user_id: str, analysis: ScheduledCompetitorAnalysis) -> dict:
        analysis.id = str(uuid4())
        await self._check_conflict(user_id, "competitor_analysis", analysis.day_of_week, analysis.time_of_day)
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"competitor_analysis": analysis.dict(exclude_unset=True)}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def add_interaction_date_by_user_id(self, user_id: str, date: Date) -> dict:
        date.id = str(uuid4())
        await self._check_conflict(user_id, "interaction_analysis_dates", date.day_of_week, date.time_of_day)
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)},
            {"$push": {"interaction_analysis_dates": date.dict(exclude_unset=True)}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    # ---------------- Update nested items ---------------- #

    async def update_post(self, user_id: str, post_id: str, update_data: dict) -> dict:
        # If day/time is being updated, check conflict
        new_day = update_data.get("day_of_week")
        new_time = update_data.get("time_of_day")
        if new_day and new_time:
            await self._check_conflict(user_id, "posts", new_day, new_time, exclude_id=post_id)

        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id), "posts.id": post_id},
            {"$set": {f"posts.$.{k}": v for k, v in update_data.items()}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_competitor_analysis(self, user_id: str, analysis_id: str, update_data: dict) -> dict:
        new_day = update_data.get("day_of_week")
        new_time = update_data.get("time_of_day")
        if new_day and new_time:
            await self._check_conflict(user_id, "competitor_analysis", new_day, new_time, exclude_id=analysis_id)

        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id), "competitor_analysis.id": analysis_id},
            {"$set": {f"competitor_analysis.$.{k}": v for k, v in update_data.items()}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_interaction_date(self, user_id: str, date_id: str, update_data: dict) -> dict:
        new_day = update_data.get("day_of_week")
        new_time = update_data.get("time_of_day")
        if new_day and new_time:
            await self._check_conflict(user_id, "interaction_analysis_dates", new_day, new_time, exclude_id=date_id)

        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id), "interaction_analysis_dates.id": date_id},
            {"$set": {f"interaction_analysis_dates.$.{k}": v for k, v in update_data.items()}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}
