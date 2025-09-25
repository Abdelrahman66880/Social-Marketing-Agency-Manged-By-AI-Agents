# user_model.py
from .BaseModel import BaseModel
from .db_schemas import User
from .enums.UserEnums import AccountStatus
from .enums.DBEnums import DBEnums
from bson.objectid import ObjectId
from typing import List, Optional
from .BuisnessInfoModel import BusinessInfoModel
from .ScheduleModel import ScheduleModel
from .RecommendationModel import RecommendationModel
from .NotificationModel import NotificationModel


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
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                    sparse=index.get("sparse", False)
                )

    # ---------------- CRUD ---------------- #

    async def create_user(self, user: User) -> User:
        result = await self.collection.insert_one(user.dict(by_alias=True, exclude_unset=True))
        user.id = result.inserted_id
        return user

    async def get_by_user_id(self, user_id: str) -> Optional[User]:
        result = await self.collection.find_one({"_id": ObjectId(user_id)})
        return User(**result) if result else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        result = await self.collection.find_one({"email": email})
        return User(**result) if result else None

    async def update_user_status_by_id(self, user_id: str, new_status: AccountStatus) -> dict:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"accountStatus": new_status.value}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_user_username_by_id(self, user_id: str, new_username: str) -> dict:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": new_username}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_user_hash_password_by_id(self, user_id: str, new_hash: str) -> dict:
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"hashPassword": new_hash}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_user_by_id(self, user_id: str) -> dict:
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count:
            business_model = await BusinessInfoModel.create_instance(self.db_client)
            schedule_model = await ScheduleModel.create_instance(self.db_client)
            recommendation_model = await RecommendationModel.create_instance(self.db_client)
            notification_model = await NotificationModel.create_instance(self.db_client)

            await business_model.delete_by_user_id(user_id)
            await schedule_model.delete_by_user_id(user_id)
            await recommendation_model.delete_recommendations_by_user_id(user_id)
            await notification_model.delete_notifications_by_user_id(user_id)
            
    async def delete_many_by_filter(self, filter: dict) -> dict:
        users = await self.collection.find(filter, {"_id": 1}).to_list(None)
        user_ids = [u["_id"] for u in users]

        if not user_ids:
            return {"deleted_count": 0, "related_deleted": {}}

        result = await self.collection.delete_many(filter)

        business_info_model = BusinessInfoModel(self.db_client)
        schedule_model = ScheduleModel(self.db_client)
        recommendation_model = RecommendationModel(self.db_client)
        notification_model = NotificationModel(self.db_client)

        related_deleted = {}

        related_deleted["business_infos"] = (
            await business_info_model.delete_many_by_filter({"user_id": {"$in": user_ids}})
        )["deleted_count"]

        related_deleted["schedules"] = (
            await schedule_model.delete_many_by_filter({"user_id": {"$in": user_ids}})
        )["deleted_count"]

        related_deleted["recommendations"] = (
            await recommendation_model.delete_many_by_filter({"user_id": {"$in": user_ids}})
        )["deleted_count"]

        related_deleted["notifications"] = (
            await notification_model.delete_many_by_filter({"user_id": {"$in": user_ids}})
        )["deleted_count"]

        return {
            "deleted_count": result.deleted_count,
            "related_deleted": related_deleted
        }


    # ---------------- Utility ---------------- #

    async def exists_by_username(self, username: str) -> bool:
        result = await self.collection.find_one({"username": username}, {"_id": 1})
        return result is not None

    async def exists_by_email(self, email: str) -> bool:
        result = await self.collection.find_one({"email": email}, {"_id": 1})
        return result is not None

    async def list_users(self, page_no: int = 1, page_size: int = 20) -> List[User]:
        cursor = self.collection.find().skip((page_no - 1) * page_size).limit(page_size)
        results = await cursor.to_list(length=page_size)
        return [User(**doc) for doc in results]
    
    async def count_users_by_filter(self, filter: dict = None) -> int:
        """
        Count the number of users in the collection.
        
        :param filter: Optional filter to count only matching users (default: all users).
        :return: Number of users.
        """
        filter = filter or {}
        count = await self.collection.count_documents(filter)
        return count

