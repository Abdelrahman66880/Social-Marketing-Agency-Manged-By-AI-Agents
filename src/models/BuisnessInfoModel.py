# business_info_model.py
from typing import Optional, List, Any
from bson import ObjectId
from src.models.BaseModel import BaseModel
from src.models.db_schemas import BuisnessInfo
from src.models.enums.DBEnums import DBEnums


class BusinessInfoModel(BaseModel):
    """
    Repository layer for managing the BusinessInfo collection in MongoDB.

    This class provides CRUD operations and custom queries for the
    BusinessInfo documents. It ensures async, non-blocking operations
    with Motor and enforces indexes as defined in the schema.
    """

    def __init__(self, db_client):
        """
        Initialize the BusinessInfoModel with a MongoDB client.

        Args:
            db_client (object): The MongoDB client instance for database operations.
        """
        super().__init__(db_client)
        self.collection = self.db[DBEnums.COLLECTION_BUSINESS_INFO_NAME.value]

    # ---------------- Init ---------------- #

    @classmethod
    async def create_instance(cls, db_client: object) -> "BusinessInfoModel":
        """
        Asynchronously create and initialize a BusinessInfoModel instance.

        Ensures the business info collection and its indexes are set up
        before returning the instance.

        Args:
            db_client (object): The MongoDB client instance.

        Returns:
            BusinessInfoModel: An initialized BusinessInfoModel instance.
        """
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self) -> None:
        """
        Initialize the business info collection in the database.

        - Checks if the collection exists; if not, creates it.
        - Applies indexes as defined in the BuisnessInfo schema.
        """
        all_collections = await self.db_client.list_collection_names()
        if DBEnums.COLLECTION_BUSINESS_INFO_NAME.value not in all_collections:
            self.collection = self.db_client[DBEnums.COLLECTION_BUSINESS_INFO_NAME.value]
            indexes = BuisnessInfo.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"],
                    sparse=index.get("sparse", False),
                )

    # ---------------- CRUD ---------------- #

    async def create_business_info(self, business_info: BuisnessInfo) -> BuisnessInfo:
        """
        Insert a new BusinessInfo document into the collection.

        Args:
            business_info (BuisnessInfo): The BusinessInfo object to insert.

        Returns:
            BuisnessInfo: The inserted object with its MongoDB ID set.
        """
        result = await self.collection.insert_one(
            business_info.dict(by_alias=True, exclude_unset=True)
        )
        business_info.id = result.inserted_id
        return business_info

    async def get_by_user_id(self, user_id: str) -> Optional[BuisnessInfo]:
        """
        Fetch a BusinessInfo document by user_id (1:1 relation with User).

        Args:
            user_id (str): The string representation of the user's ObjectId.

        Returns:
            Optional[BuisnessInfo]: The BusinessInfo object if found, otherwise None.
        """
        result = await self.collection.find_one({"user_id": ObjectId(user_id)})
        return BuisnessInfo(**result) if result else None

    async def get_by_page_id(self, page_id: str) -> Optional[BuisnessInfo]:
        """
        Fetch a BusinessInfo document by facebook_page_id.

        Args:
            page_id (str): The Facebook Page ID.

        Returns:
            Optional[BuisnessInfo]: The BusinessInfo object if found, otherwise None.
        """
        result = await self.collection.find_one({"facebook_page_id": page_id})
        return BuisnessInfo(**result) if result else None

    async def update_business_info(self, user_id: str, update_data: dict) -> dict:
        """
        Update fields of a BusinessInfo document for a user.

        Supports partial updates; pass only the fields you want changed.

        Args:
            user_id (str): The string representation of the user's ObjectId.
            update_data (dict): Fields and values to update.

        Returns:
            dict: Contains 'matched_count' and 'modified_count'.
        """
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)}, {"$set": update_data}
        )
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
        }

    async def delete_by_user_id(self, user_id: str) -> dict:
        """
        Delete BusinessInfo documents for a given user_id (cascade delete).

        Args:
            user_id (str): The string representation of the user's ObjectId.

        Returns:
            dict: Contains 'deleted_count' indicating the number of deleted docs.
        """
        result = await self.collection.delete_many({"user_id": ObjectId(user_id)})
        return {"deleted_count": result.deleted_count}

    # ---------------- Queries ---------------- #

    async def list_business_info(
        self, page_no: int = 1, page_size: int = 20
    ) -> List[BuisnessInfo]:
        """
        Retrieve a paginated list of all BusinessInfo documents.

        Args:
            page_no (int, optional): The page number to retrieve. Defaults to 1.
            page_size (int, optional): Number of documents per page. Defaults to 20.

        Returns:
            List[BuisnessInfo]: A list of BusinessInfo objects for the specified page.
        """
        cursor = (
            self.collection.find()
            .skip((page_no - 1) * page_size)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)
        return [BuisnessInfo(**doc) for doc in results]

    async def list_by_field(
        self, field: str, page_no: int = 1, page_size: int = 20
    ) -> List[BuisnessInfo]:
        """
        List all businesses that belong to a given field.

        Args:
            field (str): The business field to filter by.
            page_no (int, optional): The page number to retrieve. Defaults to 1.
            page_size (int, optional): Number of documents per page. Defaults to 20.

        Returns:
            List[BuisnessInfo]: A list of matching BusinessInfo objects.
        """
        cursor = (
            self.collection.find({"field": field})
            .skip((page_no - 1) * page_size)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)
        return [BuisnessInfo(**doc) for doc in results]

    async def search_by_keyword(
        self, keyword: str, page_no: int = 1, page_size: int = 20
    ) -> List[BuisnessInfo]:
        """
        Search BusinessInfo documents by keyword (case-insensitive).

        Looks for matches inside the businessKeyWords array.

        Args:
            keyword (str): The keyword to search for.
            page_no (int, optional): The page number. Defaults to 1.
            page_size (int, optional): Number of documents per page. Defaults to 20.

        Returns:
            List[BuisnessInfo]: A list of BusinessInfo objects matching the keyword.
        """
        cursor = (
            self.collection.find(
                {"businessKeyWords": {"$regex": keyword, "$options": "i"}}
            )
            .skip((page_no - 1) * page_size)
            .limit(page_size)
        )
        results = await cursor.to_list(length=page_size)
        return [BuisnessInfo(**doc) for doc in results]

    async def exists_for_user(self, user_id: str) -> bool:
        """
        Check if a user already has a BusinessInfo document.

        Args:
            user_id (str): The string representation of the user's ObjectId.

        Returns:
            bool: True if exists, False otherwise.
        """
        result = await self.collection.find_one(
            {"user_id": ObjectId(user_id)}, {"_id": 1}
        )
        return result is not None

    async def add_to_list_field(
        self, user_id: str, field_name: str, value: Any
    ) -> dict:
        """
        Append a value to any list field in BusinessInfo.

        Uses $addToSet to avoid duplicates.
        Example: add keyword, goal, differentiator, etc.

        Args:
            user_id (str): The string representation of the user's ObjectId.
            field_name (str): The list field name to update.
            value (Any): The value to append.

        Returns:
            dict: Contains 'matched_count' and 'modified_count'.
        """
        result = await self.collection.update_one(
            {"user_id": ObjectId(user_id)}, {"$addToSet": {field_name: value}}
        )
        return {
            "matched_count": result.matched_count,
            "modified_count": result.modified_count,
        }
