# user_model.py
from .BaseModel import BaseModel
from .db_schemas import User
from .enums.UserEnums import AccountStatus
from .enums.DBEnums import DBEnums
from bson.objectid import ObjectId
from typing import List, Optional
from .BuisnessInfoModel import BusinessInfoModel  # import your BusinessInfo model


class UserModel(BaseModel):

    def __init__(self, db_client):
        """
        Initialize the UserModel with a MongoDB client.

        Args:
            db_client (object): The MongoDB client instance for database operations.
        """
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_USER_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        """
        Asynchronously create and initialize a UserModel instance.

        Ensures the user collection and its indexes are set up before returning the instance.

        Args:
            db_client (object): The MongoDB client instance.

        Returns:
            UserModel: An initialized UserModel instance.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        """
        Initialize the user collection in the database.

        Checks if the user collection exists; if not, creates it and sets up the necessary indexes
        as defined in the User schema.
        """
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
        """
        Insert a new user document into the user collection.

        Args:
            user (User): The User object to be inserted.

        Returns:
            User: The inserted User object with its MongoDB ID set.
        """
        result = await self.collection.insert_one(user.dict(by_alias=True, exclude_unset=True))
        user.id = result.inserted_id
        return user

    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """
        Retrieve a single user document by its unique ID.

        Args:
            user_id (str): The string representation of the user's ObjectId.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        result = await self.collection.find_one({"_id": ObjectId(user_id)})
        return User(**result) if result else None

    async def get_user_by_email(self, email: str) -> Optional[User]:
        """
        Retrieve a user document by email address.

        Args:
            email (str): The email address to search for.

        Returns:
            Optional[User]: The User object if found, otherwise None.
        """
        result = await self.collection.find_one({"email": email})
        return User(**result) if result else None

    async def update_user_status_by_id(self, user_id: str, new_status: AccountStatus) -> dict:
        """
        Update the account status of a user by their unique ID.

        Args:
            user_id (str): The string representation of the user's ObjectId.
            new_status (AccountStatus): The new account status to set.

        Returns:
            dict: Contains 'matched_count' and 'modified_count' indicating the update result.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"accountStatus": new_status.value}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_user_username_by_id(self, user_id: str, new_username: str) -> dict:
        """
        Update the username of a user by their unique ID.

        Args:
            user_id (str): The string representation of the user's ObjectId.
            new_username (str): The new username to set.

        Returns:
            dict: Contains 'matched_count' and 'modified_count' indicating the update result.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"username": new_username}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def update_user_hash_password_by_id(self, user_id: str, new_hash: str) -> dict:
        """
        Update the hashed password of a user by their unique ID.

        Args:
            user_id (str): The string representation of the user's ObjectId.
            new_hash (str): The new hashed password to set.

        Returns:
            dict: Contains 'matched_count' and 'modified_count' indicating the update result.
        """
        result = await self.collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"hashPassword": new_hash}}
        )
        return {"matched_count": result.matched_count, "modified_count": result.modified_count}

    async def delete_user_by_id(self, user_id: str) -> dict:
        """
        Delete a user document by its unique ID.

        Args:
            user_id (str): The string representation of the user's ObjectId.

        Returns:
            dict: Contains 'deleted_count' indicating the number of deleted documents.
        """
        result = await self.collection.delete_one({"_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}

    async def delete_many_by_filter(self, filter: dict) -> dict:
        """
        Delete multiple user documents matching a filter.

        Args:
            filter (dict): The filter criteria for deletion.

        Returns:
            dict: Contains 'deleted_count' indicating the number of deleted documents.
        """
        result = await self.collection.delete_many(filter)
        return {"deleted_count": result.deleted_count}

    # ---------------- Utility ---------------- #

    async def exists_by_username(self, username: str) -> bool:
        """
        Check if a user exists with the specified username.

        Args:
            username (str): The username to check.

        Returns:
            bool: True if a user exists with the given username, False otherwise.
        """
        result = await self.collection.find_one({"username": username}, {"_id": 1})
        return result is not None

    async def exists_by_email(self, email: str) -> bool:
        """
        Check if a user exists with the specified email address.

        Args:
            email (str): The email address to check.

        Returns:
            bool: True if a user exists with the given email, False otherwise.
        """
        result = await self.collection.find_one({"email": email}, {"_id": 1})
        return result is not None

    async def list_users(self, page_no: int = 1, page_size: int = 20) -> List[User]:
        """
        List user documents with pagination support.

        Args:
            page_no (int, optional): The page number to retrieve. Defaults to 1.
            page_size (int, optional): The number of users per page. Defaults to 20.

        Returns:
            List[User]: A list of User objects for the specified page.
        """
        cursor = self.collection.find().skip((page_no - 1) * page_size).limit(page_size)
        results = await cursor.to_list(length=page_size)
        return [User(**doc) for doc in results]
    
    async def count_users_by_filter(self, filter: dict = None) -> int:
        """
        Count the number of users in the collection matching a filter.

        Args:
            filter (dict, optional): Filter to count only matching users (default: all users).

        Returns:
            int: Number of users matching the filter.
        """
        filter = filter or {}
        count = await self.collection.count_documents(filter)
        return count

